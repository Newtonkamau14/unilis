"""
grader.py
----------
Central orchestrator. Routes to the correct pipeline based on QuestionType.

PIPELINE DECISION TREE:
                        [GradingRequest]
                              |
                    question_type check
                    /                 \
            MCQ                    SHORT_ANSWER
             |                          |
        MCQGrader                  preprocess()
             |                          |
        MCQResult                  BERTEncoder
             |                    /          \
        FeedbackReport   TokenEmbeddings  SentenceEmbeddings
                              |                   |
                       TerminologyScorer    SemanticScorer
                              |                   |
                       MissingTerms          SemanticScore
                              \                  /
                           ScoreAggregator (weighted)
                                    |
                              FinalWeightedScore
                                    |
                             FeedbackReport
"""

from __future__ import annotations
from data.keyword_store import load_keywords
from models.schemas import (
    GradingRequest, GradingResponse, QuestionType,
    TerminologyScore, SemanticScore, MCQResult,
)
from modules import (
    preprocess, BERTEncoder, extract_terms,
    TerminologyScorer, SemanticScorer, ScoreAggregator,
    MCQGrader, FeedbackGenerator,
)


class ASAGGrader:
    """
    Automated Short Answer Grading service.
    Handles both SHORT_ANSWER and MULTIPLE_CHOICE question types.
    """

    def __init__(
        self,
        terminology_weight: float = 0.40,
        semantic_weight: float = 0.60,
        bert_model: str = "all-MiniLM-L6-v2",
    ):
        self.encoder = BERTEncoder(model_name=bert_model)
        self.terminology_scorer = TerminologyScorer(encoder=self.encoder)
        self.semantic_scorer = SemanticScorer(encoder=self.encoder)
        self.aggregator = ScoreAggregator(terminology_weight, semantic_weight)
        self.mcq_grader = MCQGrader()
        self.feedback_gen = FeedbackGenerator()

    def grade(self, request: GradingRequest) -> GradingResponse:
        """
        Main entry point. Routes to MCQ or Short Answer pipeline.
        """
        if request.question_type == QuestionType.MULTIPLE_CHOICE:
            return self._grade_mcq(request)
        else:
            return self._grade_short_answer(request)

    # ------------------------------------------------------------------ #
    #  MCQ PIPELINE                                                        #
    # ------------------------------------------------------------------ #
    def _grade_mcq(self, request: GradingRequest) -> GradingResponse:
        result = self.mcq_grader.grade(
            student_answer=request.student_answer,
            reference_answer=request.reference_answer,
            mcq_options=request.mcq_options,
        )
        feedback = self.feedback_gen.generate_mcq_feedback(
            is_correct=result["is_correct"],
            selected_option=result["selected_option"],
            correct_option=result["correct_option"],
        )
        return GradingResponse(
            question_type=QuestionType.MULTIPLE_CHOICE,
            final_weighted_score=result["score"],
            mcq_result=MCQResult(**result),
            feedback_report=feedback,
        )

    # ------------------------------------------------------------------ #
    #  SHORT ANSWER PIPELINE                                               #
    # ------------------------------------------------------------------ #
    def _grade_short_answer(self, request: GradingRequest) -> GradingResponse:
        # 1. Preprocess
        processed = preprocess(
            question_context=request.question_context,
            reference_answer=request.reference_answer,
            student_answer=request.student_answer,
        )

        # 2. Load keyword list (domain-specific, from data/)
        keyword_list = load_keywords(context=request.question_context)

        # 3. Extract reference terms (POS tagging)
        reference_terms = extract_terms(
            text=processed["cleaned_reference"],
            keyword_list=keyword_list,
        )

        # 4. Terminology scoring (token embeddings)
        term_result = self.terminology_scorer.score(
            reference_terms=reference_terms,
            student_tokens=processed["student_tokens"],
        )

        # 5. Semantic scoring (sentence embeddings)
        sem_result = self.semantic_scorer.score(
            reference_answer=processed["raw_reference"],
            student_answer=processed["raw_student"],
        )

        # 6. Aggregate scores
        final_score = self.aggregator.aggregate(
            terminology_score=term_result["score"],
            semantic_score=sem_result["score"],
        )

        # 7. Generate feedback
        feedback = self.feedback_gen.generate_short_answer_feedback(
            final_score=final_score,
            terminology_score=term_result["score"],
            semantic_score=sem_result["score"],
            missing_terms=term_result["missing_terms"],
        )

        return GradingResponse(
            question_type=QuestionType.SHORT_ANSWER,
            final_weighted_score=final_score,
            terminology_score=TerminologyScore(
                score=term_result["score"],
                matched_terms=term_result["matched_terms"],
                missing_terms=term_result["missing_terms"],
            ),
            semantic_score=SemanticScore(
                score=sem_result["score"],
                similarity_explanation=sem_result["similarity_explanation"],
            ),
            missing_term_report=term_result["missing_terms"],  # SHORT_ANSWER only
            feedback_report=feedback,
        )