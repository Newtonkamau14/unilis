from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from shared.schemas import (
    IngestionResponse,
    IngestionData
)

from pdf_utils import (
    validate_pdf,
    pdf_to_images
)

from pathlib import Path
import shutil
import uuid
import logging
import os
import time


# =====================================================
# CONFIGURATION
# =====================================================

SERVICE_NAME = "ingestion"

BASE_STORAGE = Path(
    os.getenv(
        "STORAGE_PATH",
        "../STORAGE"
    )
)

INPUT_DIR = BASE_STORAGE / "input"

INPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

MAX_FILE_SIZE_MB = 50


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s - "
        "%(levelname)s - "
        "%(message)s"
    )
)

logger = logging.getLogger(__name__)


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="Medical AI Ingestion Service",
    version="1.1.0"
)


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():
    return {
        "service": SERVICE_NAME,
        "status": "healthy"
    }


# =====================================================
# PDF UPLOAD
# =====================================================

@app.post(
    "/upload",
    response_model=IngestionResponse
)
async def upload_pdf(
    file: UploadFile = File(...)
):
    start_time = time.time()

    try:

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Missing filename"
            )

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )

        file_bytes = await file.read()

        file_size_mb = (
            len(file_bytes)
            / (1024 * 1024)
        )

        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=413,
                detail=(
                    f"File exceeds "
                    f"{MAX_FILE_SIZE_MB} MB limit"
                )
            )

        validate_pdf(file_bytes)

        submission_id = str(
            uuid.uuid4()
        )

        submission_dir = (
            INPUT_DIR
            / submission_id
        )

        submission_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        pdf_path = (
            submission_dir
            / file.filename
        )

        with open(
            pdf_path,
            "wb"
        ) as pdf_file:

            pdf_file.write(
                file_bytes
            )

        pages_dir = (
            submission_dir
            / "pages"
        )

        image_paths = pdf_to_images(
            pdf_path=str(pdf_path),
            output_folder=str(
                pages_dir
            ),
            dpi=300
        )

        processing_time = (
            time.time()
            - start_time
        )

        logger.info(
            f"[{submission_id}] "
            f"PDF saved and processed "
            f"({len(image_paths)} pages) "
            f"in "
            f"{processing_time:.2f}s"
        )

        return IngestionResponse(
            status="success",
            data=IngestionData(
                submission_id=submission_id,
                original_filename=file.filename,
                pdf_path=str(pdf_path),
                image_paths=image_paths,
                page_count=len(
                    image_paths
                )
            ),
            error=None
        )

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(
            f"Upload failed: {e}"
        )

        return IngestionResponse(
            status="error",
            data=None,
            error=str(e)
        )