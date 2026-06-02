from fastapi import FastAPI
from shared.schemas import (
    ExplainRequest,
    ExplainResponse,
    ExplainData
)

app = FastAPI()


@app.post("/explain", response_model=ExplainResponse)
def explain(request: ExplainRequest):
    try:
        return ExplainResponse(
            status="success",
            data=ExplainData(
                heatmap_path="storage/output/gradcam.png",
                feedback="Incorrect labeling of artery"
            ),
            error=None
        )

    except Exception as e:
        return ExplainResponse(
            status="error",
            data=None,
            error=str(e)
        )
