import os


INGESTION_URL = os.getenv(
    "INGESTION_URL",
    "http://ingestion:8001"
)

OCR_URL = os.getenv(
    "OCR_URL",
    "http://ocr:8002"
)

DETECTION_URL = os.getenv(
    "DETECTION_URL",
    "http://detection:8003"
)

SCORING_URL = os.getenv(
    "SCORING_URL",
    "http://scoring:8004"
)

EXPLAINABILITY_URL = os.getenv(
    "EXPLAINABILITY_URL",
    "http://explainability:8005"
)

REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT",
        "300"
    )
)