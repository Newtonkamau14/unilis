from fastapi import FastAPI, UploadFile, File
import requests
import shutil
import os

app = FastAPI()

STORAGE_PATH = "../storage/input"


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    file_path = os.path.join(STORAGE_PATH, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Call ingestion
    response = requests.post(
        "http://ingestion:8000/process",
        json={"file_path": file_path}
    )

    return response.json()
