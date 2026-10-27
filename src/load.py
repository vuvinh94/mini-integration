import pandas as pd
import logging
import psycopg2
from io import StringIO

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


class DatabaseConnection:
    def __init__(self, config: dict):
        self.config = config
        self.conn = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                dbname=self.config["name"],
                user=self.config["user"],
                password=self.config["password"],
                connect_timeout=10,
            )
            logger.debug("Đã thiết lập kết nối đến cơ sở dữ liệu.")
            return self
        except psycopg2.OperationalError as e:
            logger.error(f"Không thể kết nối đến cơ sở dữ liệu: {e}")
            raise DatabaseError(f"Lỗi kết nối cơ sở dữ liệu: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.debug("Đã đóng kết nối cơ sở dữ liệu.")

    def truncate_table(self, table_name: str):
        with self.conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
            self.conn.commit()
        logger.info(f"Đã làm sạch (truncate) bảng: {table_name}")


def load_table_with_copy(db: DatabaseConnection, df: pd.DataFrame, table_name: str):
    """Nạp DataFrame vào PostgreSQL bằng giao thức COPY tốc độ cao."""
    if df.empty:
        logger.warning(f"Bảng {table_name} rỗng. Bỏ qua nạp dữ liệu.")
        return

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, sep="\t", na_rep="\\N", float_format="%g")
    buffer.seek(0)

    columns = ", ".join(df.columns)

    try:
        with db.conn.cursor() as cur:
            cur.copy_expert(
                f"COPY {table_name} ({columns}) FROM STDIN WITH (FORMAT CSV, DELIMITER '\t', NULL '\\N')",
                buffer,
            )
            db.conn.commit()
        logger.info(f"Đã nạp {len(df):,} dòng vào bảng {table_name} qua COPY protocol")
    except psycopg2.Error as e:
        db.conn.rollback()
        logger.error(f"Lỗi COPY cho bảng {table_name}: {e}")
        raise DatabaseError(f"Lỗi nạp bảng {table_name}: {e}") from e


def load_all(dataframes: dict, config: dict):
    tables_config = config["tables"]
    sorted_tables = sorted(tables_config.items(), key=lambda x: x[1]["load_order"])

    with DatabaseConnection(config["database"]) as db:
        for table_name, table_config in sorted_tables:
            if table_name not in dataframes:
                logger.warning(f"Không có dữ liệu cho bảng: {table_name}. Bỏ qua.")
                continue

            df = dataframes[table_name]
            logger.info(f"Đang nạp dữ liệu vào bảng: {table_name}")

            db.truncate_table(table_name)
            load_table_with_copy(db, df, table_name)

    logger.info("Đã hoàn tất nạp dữ liệu vào tất cả các bảng.")