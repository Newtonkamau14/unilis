import logging
import sys
from logging.handlers import RotatingFileHandler

from config import settings


def build_logger():

    logger = logging.getLogger(
        settings.SERVICE_NAME
    )

    logger.setLevel(
        settings.LOG_LEVEL
    )

    logger.handlers.clear()

    formatter = logging.Formatter(
        settings.LOG_FORMAT
    )

    # =====================================================
    # CONSOLE
    # =====================================================

    console_handler = logging.StreamHandler(
        sys.stdout
    )

    console_handler.setFormatter(
        formatter
    )

    # =====================================================
    # FILE
    # =====================================================

    file_handler = RotatingFileHandler(
        filename="explainability.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=10,
        encoding="utf-8"
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        console_handler
    )

    logger.addHandler(
        file_handler
    )

    logger.propagate = False

    return logger


logger = build_logger()