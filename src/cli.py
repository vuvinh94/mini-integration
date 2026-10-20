import argparse
import logging
from src.pipeline import run_pipeline
from src.logging_config import setup_logging
from src.config_loader import load_config, BASE_DIR

logger = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tiki-etl",
        description="Pipeline ETL cho dữ liệu Tiki Books E-Commerce.",
    )
    parser.add_argument("--table", "-t", type=str, default=None,
                        help="Tên bảng cần xử lý (books hoặc comments).")
    parser.add_argument("--stage", "-s", type=str,
                        choices=["extract", "transform", "load", "all"],
                        default="all", help="Giai đoạn pipeline cần chạy.")
    parser.add_argument("--log-level", "-l", type=str,
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        default="INFO", help="Mức độ logging.")
    parser.add_argument("--config", "-c", type=str, default=None,
                        help="Đường dẫn đến file cấu hình YAML.")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    log_dir = BASE_DIR / "logs"
    setup_logging(log_dir, args.log_level)

    logger.info("=" * 60)
    logger.info("BẮT ĐẦU PIPELINE ETL - TIKI BOOKS DATASET")
    logger.info(f"Tham số: table={args.table}, stage={args.stage}")
    logger.info("=" * 60)

    try:
        config = load_config(args.config)
        run_pipeline(config, table=args.table, stage=args.stage)
        logger.info("Pipeline hoàn tất thành công.")
    except Exception as e:
        logger.exception("Pipeline thất bại:")
        raise SystemExit(1)


if __name__ == "__main__":
    main()