import logging
from pathlib import Path


LOG_DIR = Path("logs")

LOG_DIR.mkdir(
    exist_ok=True
)


logger = logging.getLogger(
    "gateway"
)

logger.setLevel(
    logging.INFO
)


formatter = logging.Formatter(
    "%(asctime)s - "
    "%(levelname)s - "
    "%(message)s"
)


gateway_handler = logging.FileHandler(
    LOG_DIR / "gateway.log"
)

gateway_handler.setFormatter(
    formatter
)


error_handler = logging.FileHandler(
    LOG_DIR / "errors.log"
)

error_handler.setFormatter(
    formatter
)


console_handler = logging.StreamHandler()

console_handler.setFormatter(
    formatter
)


logger.addHandler(
    gateway_handler
)

logger.addHandler(
    error_handler
)

logger.addHandler(
    console_handler
)