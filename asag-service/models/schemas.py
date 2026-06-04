from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class QuestionType(str, Enum):
    SHORT_ANSWER = "short_answer"
    MULTIPLE_CHOICE = "multiple_choice"


class GradingRequest(BaseModel):
    question_context: str = Field(..., description="The question being asked")
    reference_answer: str = Field(..., description="The model/correct answer")
    student_answer: str = Field(..., description="The student's submitted answer")
    question_type: QuestionType = Field(
        default=QuestionType.SHORT_ANSWER,
        description="Type of question — determines grading pipeline used"
    )
    mcq_options: Optional[list[str]] = Field(
        default=None,
        description="For MCQ only: list of answer choices e.g. ['A. ...', 'B. ...']"
    )


class TerminologyScore(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    matched_terms: list[str]
    missing_terms: list[str]  # only populated for short_answer


class SemanticScore(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    similarity_explanation: str


class MCQResult(BaseModel):
    is_correct: bool
    selected_option: str
    correct_option: str
    score: float  # 0.0 or 1.0


class GradingResponse(BaseModel):
    question_type: QuestionType
    final_weighted_score: float = Field(..., ge=0.0, le=1.0)

    # Short answer fields
    terminology_score: Optional[TerminologyScore] = None
    semantic_score: Optional[SemanticScore] = None
    missing_term_report: Optional[list[str]] = None  # only for short_answer

    # MCQ field
    mcq_result: Optional[MCQResult] = None

    feedback_report: str