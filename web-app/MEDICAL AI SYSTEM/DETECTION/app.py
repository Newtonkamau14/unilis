from fastapi import FastAPI
from shared.schemas import (
    DetectionRequest,
    DetectionResponse,
    DetectionData,
    Detection,
    BoundingBox
)

app = FastAPI()


@app.post("/detect", response_model=DetectionResponse)
def detect(request: DetectionRequest):
    try:
        detections = [
            Detection(
                label="heart",
                bbox=BoundingBox(x1=10, y1=20, x2=100, y2=200),
                confidence=0.95
            )
        ]

        return DetectionResponse(
            status="success",
            data=DetectionData(
                detections=detections,
                segmentation_mask="storage/output/mask.png"
            ),
            error=None
        )

    except Exception as e:
        return DetectionResponse(
            status="error",
            data=None,
            error=str(e)
        )
