from fastapi import FastAPI
from shared.schemas import (
    ScoringRequest,
    ScoringResponse,
    ScoringData
)

app = FastAPI()


@app.post("/score", response_model=ScoringResponse)
def score(request: ScoringRequest):
    try:
        return ScoringResponse(
            status="success",
            data=ScoringData(
                final_score=0.82,
                label_accuracy=0.88,
                structure_accuracy=0.79
            ),
            error=None
        )

    except Exception as e:
        return ScoringResponse(
            status="error",
            data=None,
            error=str(e)
        )
