import requests

from config import (
    INGESTION_URL,
    OCR_URL,
    DETECTION_URL,
    SCORING_URL,
    EXPLAINABILITY_URL,
    REQUEST_TIMEOUT
)

from logger import logger


SERVICES = {
    "ingestion": INGESTION_URL,
    "ocr": OCR_URL,
    "detection": DETECTION_URL,
    "scoring": SCORING_URL,
    "explainability": EXPLAINABILITY_URL
}


def check_services():

    status = {}

    for name, url in SERVICES.items():

        try:

            response = requests.get(
                f"{url}/health",
                timeout=5
            )

            status[name] = (
                "healthy"
                if response.status_code == 200
                else "unhealthy"
            )

        except Exception:

            status[name] = "offline"

    return status


async def submit_to_ingestion(
    file
):

    file_content = await file.read()

    files = {
        "file": (
            file.filename,
            file_content,
            "application/pdf"
        )
    }

    response = requests.post(
        f"{INGESTION_URL}/upload",
        files=files,
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code != 200:

        raise Exception(
            f"Ingestion service failed: "
            f"{response.text}"
        )

    logger.info(
        f"Uploaded PDF: "
        f"{file.filename}"
    )

    return response.json()