import pandas as pd
import numpy as np
import logging
from src.validation import validate_dataframe

logger = logging.getLogger(__name__)


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Cắt khoảng trắng dư thừa và chuyển các giá trị rỗng/nan về None."""
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": None, "None": None, "": None})
    return df


def transform_books(df: pd.DataFrame) -> pd.DataFrame:
    """Làm sạch và chuyển đổi dữ liệu sách Tiki."""
    logger.info("Đang chuyển đổi bảng: books")
    df = df.copy()

    # Đổi tên cột sai chính tả từ nguồn cào nếu có
    if "catagory" in df.columns:
        df = df.rename(columns={"catagory": "category"})

    # Dùng mã sản phẩm Tiki làm id để khớp với comments.product_id
    df = df.rename(columns={"product_id": "id"})

    df = _strip_strings(df)

    df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")

    # Ép kiểu các cột số nguyên
    numeric_int_cols = ["quantity", "n_review", "pages"]
    for col in numeric_int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df["original_price"] = pd.to_numeric(df["original_price"], errors="coerce")
    df["current_price"] = pd.to_numeric(df["current_price"], errors="coerce")
    df["avg_rating"] = pd.to_numeric(df["avg_rating"], errors="coerce")

    # Loại bỏ bản ghi thiếu id, tiêu đề hoặc thiếu giá bán
    df = df.dropna(subset=["id", "title", "current_price"])

    # Khử trùng lặp theo id sản phẩm
    before = len(df)
    df = df.drop_duplicates(subset=["id"])
    if len(df) < before:
        logger.info(f"Đã loại bỏ {before - len(df)} dòng sách bị trùng lặp")

    # Tính toán tỷ lệ giảm giá (discount_percent)
    df["discount_percent"] = np.where(
        (df["original_price"].notna()) & (df["original_price"] > 0),
        np.round(((df["original_price"] - df["current_price"]) / df["original_price"]) * 100, 2),
        0.0,
    )
    # Giới hạn discount_percent trong khoảng từ 0% đến 100%
    df["discount_percent"] = df["discount_percent"].clip(lower=0.0, upper=100.0)

    df = df.reset_index(drop=True)

    # Sắp xếp lại thứ tự cột khớp với schema database
    target_columns = [
        "id", "title", "authors", "original_price", "current_price",
        "discount_percent", "quantity", "category", "n_review",
        "avg_rating", "pages", "manufacturer", "cover_link"
    ]
    df = df[[col for col in target_columns if col in df.columns]]

    df = validate_dataframe(df, "books")
    logger.info(f"Hoàn thành chuyển đổi bảng books: {len(df):,} dòng")
    return df


def transform_comments(df: pd.DataFrame, book_ids: pd.Series = None) -> pd.DataFrame:
    """Làm sạch và chuyển đổi dữ liệu nhận xét/đánh giá Tiki.

    Nếu truyền book_ids, chỉ giữ các bình luận có product_id nằm trong book_ids.
    """
    logger.info("Đang chuyển đổi bảng: comments")
    df = df.copy()
    df = _strip_strings(df)

    # Ép kiểu các cột số
    df["comment_id"] = pd.to_numeric(df["comment_id"], errors="coerce").astype("Int64")
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce").astype("Int64")
    df["customer_id"] = pd.to_numeric(df["customer_id"], errors="coerce").astype("Int64")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").astype("Int64")
    df["thank_count"] = pd.to_numeric(df["thank_count"], errors="coerce").fillna(0).astype("Int64")

    # Loại bỏ bản ghi thiếu comment_id, product_id hoặc rating
    df = df.dropna(subset=["comment_id", "product_id", "rating"])

    # Khử trùng lặp theo comment_id
    before = len(df)
    df = df.drop_duplicates(subset=["comment_id"])
    if len(df) < before:
        logger.info(f"Đã loại bỏ {before - len(df)} bình luận bị trùng lặp")

    # Giữ điểm rating trong khoảng hợp lệ [1, 5]
    df = df[(df["rating"] >= 1) & (df["rating"] <= 5)]

    # Loại bỏ bình luận của sản phẩm không có trong bảng books
    if book_ids is not None:
        before = len(df)
        df = df[df["product_id"].isin(book_ids)]
        if len(df) < before:
            logger.info(f"Đã loại bỏ {before - len(df)} bình luận không có sách tương ứng")

    target_columns = [
        "comment_id", "product_id", "customer_id", "rating",
        "title", "thank_count", "content"
    ]
    df = df[[col for col in target_columns if col in df.columns]]

    df = validate_dataframe(df, "comments")
    logger.info(f"Hoàn thành chuyển đổi bảng comments: {len(df):,} dòng")
    return df


TRANSFORM_MAP = {
    "books": transform_books,
    "comments": transform_comments,
}