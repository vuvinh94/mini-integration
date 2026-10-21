import logging
from src.extract import extract_table
from src.transform import TRANSFORM_MAP, transform_books, transform_comments
from src.load import load_all
from src.config_loader import BASE_DIR

logger = logging.getLogger(__name__)


def _get_book_ids(dataframes: dict, tables_config: dict, data_raw_dir):
    """Lấy danh sách id sách hợp lệ để lọc bình luận."""
    if "books" in dataframes:
        return dataframes["books"]["id"]
    # Khi chỉ chạy --table comments: đọc file sách để lấy id, không nạp bảng books
    logger.info("Đọc dữ liệu books để lọc bình luận theo product_id")
    books_df = extract_table("books", data_raw_dir / tables_config["books"]["file"])
    return transform_books(books_df)["id"]


def run_pipeline(config: dict, table: str = None, stage: str = "all"):
    tables_config = config["tables"]
    data_raw_dir = BASE_DIR / config["paths"]["data_raw"]

    if table:
        if table not in tables_config:
            raise ValueError(f"Bảng không tồn tại: {table}. Các bảng hiện có: {list(tables_config.keys())}")
        tables_to_process = {table: tables_config[table]}
        logger.info(f"Chỉ xử lý bảng: {table}")
    else:
        tables_to_process = tables_config

    dataframes = {}

    if stage in ("all", "extract"):
        logger.info("=== BƯỚC: EXTRACT (TRÍCH XUẤT) ===")
        for table_name, table_cfg in tables_to_process.items():
            file_path = data_raw_dir / table_cfg["file"]
            try:
                dataframes[table_name] = extract_table(table_name, file_path)
            except Exception as e:
                logger.error(f"Trích xuất thất bại cho bảng {table_name}: {e}")
                raise

    if stage in ("all", "transform"):
        logger.info("=== BƯỚC: TRANSFORM (CHUYỂN ĐỔI) ===")
        # Biến đổi theo load_order để books có trước comments
        for table_name in sorted(dataframes, key=lambda t: tables_config[t]["load_order"]):
            if table_name == "comments":
                book_ids = _get_book_ids(dataframes, tables_config, data_raw_dir)
                dataframes[table_name] = transform_comments(dataframes[table_name], book_ids)
            elif table_name in TRANSFORM_MAP:
                dataframes[table_name] = TRANSFORM_MAP[table_name](dataframes[table_name])

    if stage in ("all", "load"):
        logger.info("=== BƯỚC: LOAD (NẠP DỮ LIỆU) ===")
        load_all(dataframes, config)

    logger.info("Pipeline đã hoàn thành tất cả các bước.")