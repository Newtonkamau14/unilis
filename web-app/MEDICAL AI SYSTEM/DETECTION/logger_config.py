import os
import logging

from logging.handlers import RotatingFileHandler


# =====================================================
# LOG DIRECTORY
# =====================================================

LOG_DIR = "logs"

os.makedirs(
    LOG_DIR,
    exist_ok=True
)


# =====================================================
# LOG FORMAT
# =====================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

formatter = logging.Formatter(
    LOG_FORMAT
)


# =====================================================
# DETECTION LOG
# =====================================================

detection_handler = RotatingFileHandler(
    filename=os.path.join(
        LOG_DIR,
        "detection.log"
    ),
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)

detection_handler.setLevel(
    logging.INFO
)

detection_handler.setFormatter(
    formatter
)


# =====================================================
# ERROR LOG
# =====================================================

error_handler = RotatingFileHandler(
    filename=os.path.join(
        LOG_DIR,
        "errors.log"
    ),
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)

error_handler.setLevel(
    logging.ERROR
)

error_handler.setFormatter(
    formatter
)


# =====================================================
# PERFORMANCE LOG
# =====================================================

performance_handler = RotatingFileHandler(
    filename=os.path.join(
        LOG_DIR,
        "performance.log"
    ),
    maxBytes=10 * 1024 * 1024,
    backupCount=5
)

performance_handler.setLevel(
    logging.INFO
)

performance_handler.setFormatter(
    formatter
)


# =====================================================
# DETECTION LOGGER
# =====================================================

detection_logger = logging.getLogger(
    "detection"
)

detection_logger.setLevel(
    logging.INFO
)

if not detection_logger.handlers:

    detection_logger.addHandler(
        detection_handler
    )

    detection_logger.addHandler(
        error_handler
    )


# =====================================================
# PERFORMANCE LOGGER
# =====================================================

performance_logger = logging.getLogger(
    "performance"
)

performance_logger.setLevel(
    logging.INFO
)

if not performance_logger.handlers:

    performance_logger.addHandler(
        performance_handler
    )


# =====================================================
# SUBMISSION LOGGING HELPERS
# =====================================================

def log_submission_started(
    submission_id: str
):

    detection_logger.info(
        f"[{submission_id}] "
        f"Started processing"
    )


def log_submission_completed(
    submission_id: str
):

    detection_logger.info(
        f"[{submission_id}] "
        f"Completed processing"
    )


def log_submission_error(
    submission_id: str,
    error_message: str
):

    detection_logger.error(
        f"[{submission_id}] "
        f"ERROR: {error_message}"
    )


def log_image_processing(
    submission_id: str,
    image_path: str
):

    detection_logger.info(
        f"[{submission_id}] "
        f"Processing image: {image_path}"
    )


def log_detection_count(
    submission_id: str,
    image_path: str,
    count: int
):

    detection_logger.info(
        f"[{submission_id}] "
        f"Detected {count} objects "
        f"in {image_path}"
    )


def log_performance(
    submission_id: str,
    image_path: str,
    execution_time: float
):

    performance_logger.info(
        f"[{submission_id}] "
        f"Image={image_path} "
        f"ExecutionTime={execution_time:.3f}s"
    )