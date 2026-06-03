from fastapi import FastAPI
from pydantic import BaseModel
from sbert_model import embed
from scoring_logic import compute_score

app = FastAPI()


class ScoreRequest(BaseModel):
    student_text: str
    reference_text: str


@app.post("/score")
def score(req: ScoreRequest):

    student_emb = embed(
        req.student_text
    )

    ref_emb = embed(
        req.reference_text
    )

    score = compute_score(
        student_emb,
        ref_emb
    )

    return {
        "score": score
    }