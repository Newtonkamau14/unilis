from fastapi import FastAPI
from shared.schemas import IngestionRequest, IngestionResponse, IngestionData

app = FastAPI()


@app.post("/process", response_model=IngestionResponse)
def process_file(request: IngestionRequest):
    try:
        # Dummy logic (replace later)
        image_paths = ["storage/input/page_1.png"]

        return IngestionResponse(
            status="success",
            data=IngestionData(image_paths=image_paths),
            error=None
        )

    except Exception as e:
        return IngestionResponse(
            status="error",
            data=None,
            error=str(e)
        )
