from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():

    return {
        "service": "Medical AI Assessment System"
    }