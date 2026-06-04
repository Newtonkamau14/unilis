from pathlib import Path

PROJECT_NAME = "Medical AI Diagram Assessment System"

API_VERSION = "v1"

SUPPORTED_IMAGE_TYPES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff"
}

MAX_FILE_SIZE_MB = 25

CONFIDENCE_THRESHOLD = 0.30

ROOT_DIR = Path(__file__).resolve().parent.parent

STORAGE_DIR = ROOT_DIR / "STORAGE"

INPUT_DIR = STORAGE_DIR / "input"

OUTPUT_DIR = STORAGE_DIR / "output"

TEMP_DIR = ROOT_DIR / "temp"