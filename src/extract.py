import pandas as pd
import logging
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Lỗi xảy ra trong quá trình trích xuất dữ liệu."""
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((pd.errors.ParserError, IOError)),
    reraise=True,
)
def _read_csv_with_retry(filepath: Path) -> pd.DataFrame:
    """Đọc file CSV với mã hóa UTF-8 và cơ chế tự động thử lại khi gặp lỗi tạm thời."""
    logger.debug(f"Đang thử đọc file: {filepath}")
    try:
        return pd.read_csv(filepath, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(filepath, encoding="utf-8-sig")


def extract_table(table_name: str, file_path: Path) -> pd.DataFrame:
    """Trích xuất một bảng từ file CSV."""
    logger.info(f"Trích xuất bảng: {table_name} từ {file_path}")

    if not file_path.exists():
        msg = f"File không tồn tại: {file_path}"
        logger.error(msg)
        raise ExtractionError(msg)

    try:
        df = _read_csv_with_retry(file_path)
        logger.info(
            f"Đã đọc thành công bảng {table_name}: {len(df):,} dòng, {len(df.columns)} cột"
        )
        return df
    except pd.errors.EmptyDataError as e:
        logger.error(f"File rỗng: {file_path}")
        raise ExtractionError(f"File rỗng: {file_path}") from e
    except Exception as e:
        logger.error(f"Lỗi không mong muốn khi đọc file {file_path}: {e}")
        raise ExtractionError(f"Lỗi đọc file {file_path}: {e}") from e