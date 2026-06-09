import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(
    service_name: str,
    log_dir: str = "logs"
) -> logging.Logger:

    Path(log_dir).mkdir(
        parents=True,
        exist_ok=True
    )

    logger = logging.getLogger(
        service_name
    )

    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        (
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        )
    )

    file_handler = RotatingFileHandler(
        filename=f"{log_dir}/{service_name}.log",
        maxBytes=10_000_000,
        backupCount=5
    )

    file_handler.setFormatter(
        formatter
    )

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )

    return logger