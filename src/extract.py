import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Lỗi xảy ra trong quá trình trích xuất dữ liệu."""
    pass

def _read_csv(filepath: Path) -> pd.DataFrame:
    """Đọc file CSV với mã hóa UTF-8"""
    logger.debug(f"Đang thử đọc file: {filepath}")
    return pd.read_csv(filepath, encoding="utf-8")



def extract_table(table_name: str, file_path: Path) -> pd.DataFrame:
    """Trích xuất một bảng từ file CSV."""
    logger.info(f"Trích xuất bảng: {table_name} từ {file_path}")

    if not file_path.exists():
        msg = f"File không tồn tại: {file_path}"
        logger.error(msg)
        raise ExtractionError(msg)

    try:
        df = _read_csv(file_path)
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