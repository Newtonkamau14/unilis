import os
from pathlib import Path

TESSERACT_CONFIG = os.getenv(
    "TESSERACT_CONFIG",
    "--oem 3 --psm 6"
)

MIN_CONFIDENCE = float(
    os.getenv(
        "MIN_CONFIDENCE",
        "70"
    )
)

BASE_STORAGE = Path(
    os.getenv(
        "STORAGE_PATH",
        "../STORAGE"
    )
)

OCR_OUTPUT_DIR = (
    BASE_STORAGE /
    "output"
)

OCR_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)