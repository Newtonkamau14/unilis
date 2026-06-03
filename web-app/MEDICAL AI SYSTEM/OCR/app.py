from fastapi import FastAPI
from pydantic import BaseModel
from yolo_model import detect

app = FastAPI()


class DetectRequest(BaseModel):
    image_path: str


@app.post("/detect")
def run_detection(req: DetectRequest):

    labels = detect(req.image_path)

    return {
        "labels": labels
    }