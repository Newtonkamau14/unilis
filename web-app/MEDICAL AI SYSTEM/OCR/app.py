from fastapi import (
    FastAPI,
    HTTPException
)

from pathlib import Path
import time

from schemas import (
    OCRRequest,
    OCRBatchRequest
)

from ocr_model import (
    extract_text,
    extract_confidence
)

from clip_model import (
    verify_text
)

from storage import (
    save_ocr_result
)

from config import (
    MIN_CONFIDENCE
)

from logger import logger


app = FastAPI(
    title="Medical AI OCR Service",
    version="2.0.0"
)


@app.get("/health")
def health():

    return {
        "service": "ocr",
        "status": "healthy"
    }


@app.post("/extract")
def extract(req: OCRRequest):

    start_time = time.time()

    try:

        image_path = Path(
            req.image_path
        )

        if not image_path.exists():

            raise HTTPException(
                status_code=404,
                detail="Image not found"
            )

        text = extract_text(
            str(image_path)
        )

        confidence = extract_confidence(
            str(image_path)
        )

        verified = verify_text(
            text
        )

        result = {
            "status": "success",
            "submission_id": req.submission_id,
            "page_number": req.page_number,
            "image_path": str(
                image_path
            ),
            "ocr_confidence": confidence,
            "confidence_passed":
                confidence >= MIN_CONFIDENCE,
            "verified": verified,
            "text": text
        }

        save_ocr_result(
            req.submission_id,
            req.page_number,
            result
        )

        duration = (
            time.time() -
            start_time
        )

        logger.info(
            f"OCR page "
            f"{req.page_number} "
            f"processed in "
            f"{duration:.2f}s"
        )

        return result

    except Exception as e:

        logger.exception(
            f"OCR failed: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/extract-batch")
def extract_batch(
    req: OCRBatchRequest
):

    results = []

    for page in req.pages:

        image_path = Path(
            page.image_path
        )

        if not image_path.exists():
            continue

        text = extract_text(
            str(image_path)
        )

        confidence = extract_confidence(
            str(image_path)
        )

        verified = verify_text(
            text
        )

        result = {
            "status": "success",
            "submission_id":
                req.submission_id,
            "page_number":
                page.page_number,
            "image_path":
                str(image_path),
            "ocr_confidence":
                confidence,
            "confidence_passed":
                confidence >= MIN_CONFIDENCE,
            "verified":
                verified,
            "text":
                text
        }

        save_ocr_result(
            req.submission_id,
            page.page_number,
            result
        )

        results.append(
            result
        )

    return {
        "submission_id":
            req.submission_id,
        "pages_processed":
            len(results),
        "results":
            results
    }


@app.post("/process-submission")
def process_submission(
    req: OCRBatchRequest
):
    return extract_batch(
        req
    )