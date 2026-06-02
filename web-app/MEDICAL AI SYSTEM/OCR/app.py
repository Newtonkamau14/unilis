from fastapi import FastAPI
from shared.schemas import (
    OCRRequest,
    OCRResponse,
    OCRData,
    OCRText,
    BoundingBox
)

app = FastAPI()


@app.post("/extract-text", response_model=OCRResponse)
def extract_text(request: OCRRequest):
    try:
        texts = [
            OCRText(
                text="Aorta",
                bbox=BoundingBox(x1=15, y1=25, x2=80, y2=120)
            )
        ]

        return OCRResponse(
            status="success",
            data=OCRData(
                recognized_text=texts,
                embeddings=[0.1, 0.2, 0.3]
            ),
            error=None
        )

    except Exception as e:
        return OCRResponse(
            status="error",
            data=None,
            error=str(e)
        )
