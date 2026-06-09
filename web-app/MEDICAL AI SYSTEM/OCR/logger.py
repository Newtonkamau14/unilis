import logging
from pathlib import Path

LOG_DIR = Path("logs")

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(
    "ocr"
)

logger.setLevel(
    logging.INFO
)

ocr_handler = logging.FileHandler(
    LOG_DIR / "ocr.log"
)

error_handler = logging.FileHandler(
    LOG_DIR / "errors.log"
)

performance_handler = logging.FileHandler(
    LOG_DIR / "performance.log"
)

console_handler = logging.StreamHandler()

for handler in [
    ocr_handler,
    error_handler,
    performance_handler,
    console_handler
]:
    handler.setFormatter(
        formatter
    )
    logger.addHandler(
        handler
    )