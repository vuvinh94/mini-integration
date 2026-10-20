import pandera as pa
import pandas as pd
import logging
from pandera import Column, DataFrameSchema, Check

logger = logging.getLogger(__name__)

SCHEMAS = {
    "books": DataFrameSchema(
        {
            "id": Column("Int64", Check.ge(1), nullable=False, unique=True),
            "title": Column(str, Check.str_length(min_value=1), nullable=False),
            "authors": Column(str, nullable=True),
            "original_price": Column(float, Check.ge(0), nullable=True),
            "current_price": Column(float, Check.ge(0), nullable=False),
            "discount_percent": Column(float, nullable=True),
            "quantity": Column("Int64", Check.ge(0), nullable=True),
            "category": Column(str, nullable=True),
            "n_review": Column("Int64", Check.ge(0), nullable=True),
            "avg_rating": Column(float, Check.in_range(0.0, 5.0), nullable=True),
            "pages": Column("Int64", Check.ge(0), nullable=True),
            "manufacturer": Column(str, nullable=True),
            "cover_link": Column(str, nullable=True),
        },
        strict=False,
        coerce=True,
    ),
    "comments": DataFrameSchema(
        {
            "comment_id": Column("Int64", nullable=False, unique=True),
            "product_id": Column("Int64", nullable=False),
            "customer_id": Column("Int64", nullable=True),
            "rating": Column("Int64", Check.in_range(1, 5), nullable=False),
            "title": Column(str, nullable=True),
            "thank_count": Column("Int64", Check.ge(0), nullable=True),
            "content": Column(str, nullable=True),
        },
        strict=False,
        coerce=True,
    ),
}


def validate_dataframe(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Xác thực cấu trúc và chất lượng DataFrame bằng Pandera schema."""
    if table_name not in SCHEMAS:
        logger.warning(f"Không có schema xác thực cho bảng: {table_name}. Bỏ qua kiểm tra.")
        return df

    logger.info(f"Đang kiểm tra chất lượng dữ liệu bảng: {table_name}")

    try:
        validated_df = SCHEMAS[table_name].validate(df, lazy=True)
        logger.info(f"Kiểm tra chất lượng thành công cho bảng: {table_name}")
        return validated_df
    except pa.errors.SchemaErrors as e:
        logger.error(f"Xác thực thất bại cho bảng {table_name}:")
        logger.error(f"Tổng số lỗi phát hiện: {len(e.failure_cases)}")
        logger.error(f"Một số lỗi mẫu:\n{e.failure_cases.head(10)}")
        raise