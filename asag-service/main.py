from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import GradingRequest, GradingResponse
from modules.grader import ASAGGrader

app = FastAPI(
    title="ASAG Service",
    description="Automated Short Answer Grading using BERT embeddings",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate grader once at startup (loads BERT model lazily on first request)
grader = ASAGGrader(
    terminology_weight=0.40,
    semantic_weight=0.60,
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "asag-service"}


@app.post("/grade", response_model=GradingResponse)
def grade_answer(request: GradingRequest):
    """
    Grade a student's answer against a reference answer.

    - For **short_answer** questions: runs full BERT-based NLP pipeline
      (terminology + semantic scoring, missing term report, weighted aggregation).
    - For **multiple_choice** questions: runs lightweight exact-match grader,
      NO missing term report is generated.
    """
    try:
        result = grader.grade(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import json

    print("=== SHORT ANSWER TEST ===")
    sa_request = GradingRequest(
        question_context="Explain the process of photosynthesis in plants.",
        reference_answer=(
            "Photosynthesis is the process by which plants use sunlight, water, "
            "and carbon dioxide to produce glucose and oxygen through chlorophyll."
        ),
        student_answer=(
            "Plants take in sunlight and CO2 and produce food using chlorophyll "
            "in their leaves."
        ),
        question_type="short_answer",
    )
    sa_result = grader.grade(sa_request)
    print(json.dumps(sa_result.model_dump(), indent=2))

    print("\n=== MCQ TEST ===")
    mcq_request = GradingRequest(
        question_context="Which organelle is responsible for photosynthesis?",
        reference_answer="B",
        student_answer="B",
        question_type="multiple_choice",
        mcq_options=[
            "A. Mitochondria",
            "B. Chloroplast",
            "C. Nucleus",
            "D. Ribosome",
        ],
    )
    mcq_result = grader.grade(mcq_request)
    print(json.dumps(mcq_result.model_dump(), indent=2))