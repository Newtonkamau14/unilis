from datetime import datetime
from typing import Dict
from typing import List
from typing import Optional

import numpy as np

from attribution_engine import AttributionEngine
from confidence_estimator import ConfidenceEstimator
from logger import logger


class ExplanationGenerator:
    """
    Central explanation engine.

    Responsibilities:
    -----------------
    - Generate student-friendly explanations
    - Generate instructor explanations
    - Summarize attribution results
    - Summarize verification findings
    - Summarize scoring decisions
    - Produce explainability metadata
    """

    def __init__(self):
        pass

    # =====================================================
    # ATTRIBUTION EXPLANATION
    # =====================================================

    def explain_attribution(
        self,
        attribution_scores: Dict[str, float]
    ) -> str:

        try:

            if not attribution_scores:

                return (
                    "No attribution information "
                    "was available."
                )

            sorted_scores = sorted(
                attribution_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )

            most_important = (
                sorted_scores[0]
            )

            explanation = (
                f"The model focused most "
                f"strongly on "
                f"'{most_important[0]}' "
                f"with an importance score "
                f"of "
                f"{most_important[1]:.4f}. "
            )

            if len(sorted_scores) > 1:

                explanation += (
                    "Other influential "
                    "regions included "
                )

                explanation += ", ".join(
                    [
                        f"{k} ({v:.4f})"
                        for k, v
                        in sorted_scores[1:5]
                    ]
                )

                explanation += "."

            return explanation

        except Exception:

            logger.exception(
                "Attribution explanation failed"
            )

            return (
                "Unable to generate "
                "attribution explanation."
            )

    # =====================================================
    # DETECTION EXPLANATION
    # =====================================================

    def explain_detections(
        self,
        detections: List
    ) -> str:

        try:

            if not detections:

                return (
                    "No anatomical structures "
                    "were detected."
                )

            explanation = (
                f"{len(detections)} anatomical "
                f"structures were detected. "
            )

            labels = []

            for detection in detections:

                labels.append(
                    detection.label
                )

            unique_labels = list(
                set(labels)
            )

            explanation += (
                "Detected structures include: "
                + ", ".join(
                    unique_labels
                )
                + "."
            )

            return explanation

        except Exception:

            logger.exception(
                "Detection explanation failed"
            )

            return (
                "Unable to explain "
                "detected structures."
            )

    # =====================================================
    # VERIFICATION EXPLANATION
    # =====================================================

    def explain_verification(
        self,
        verification_data
    ) -> str:

        try:

            if verification_data is None:

                return (
                    "Verification results "
                    "were unavailable."
                )

            semantic_score = (
                verification_data
                .semantic_similarity
            )

            label_accuracy = (
                verification_data
                .label_accuracy
            )

            missing_labels = (
                verification_data
                .missing_labels
            )

            mismatched_labels = (
                verification_data
                .mismatched_labels
            )

            explanation = (
                f"Semantic similarity "
                f"was "
                f"{semantic_score:.2f}. "
                f"Label accuracy "
                f"was "
                f"{label_accuracy:.2f}. "
            )

            if missing_labels:

                explanation += (
                    f"Missing labels: "
                    f"{', '.join(missing_labels)}. "
                )

            if mismatched_labels:

                explanation += (
                    f"Mismatched labels: "
                    f"{', '.join(mismatched_labels)}. "
                )

            return explanation

        except Exception:

            logger.exception(
                "Verification explanation failed"
            )

            return (
                "Unable to generate "
                "verification explanation."
            )

    # =====================================================
    # SCORING EXPLANATION
    # =====================================================

    def explain_scoring(
        self,
        final_score: float,
        grade: str,
        breakdown
    ) -> str:

        try:

            explanation = (
                f"The submission achieved "
                f"a final score of "
                f"{final_score:.2f} "
                f"resulting in grade "
                f"{grade}. "
            )

            if breakdown:

                explanation += (
                    "Score contributions: "
                )

                explanation += (
                    f"Completeness "
                    f"({breakdown.completeness:.2f}), "
                    f"Structural Accuracy "
                    f"({breakdown.structural_accuracy:.2f}), "
                    f"Label Correctness "
                    f"({breakdown.label_correctness:.2f}), "
                    f"Spatial Correctness "
                    f"({breakdown.spatial_correctness:.2f}), "
                    f"Diagram Quality "
                    f"({breakdown.diagram_quality:.2f})."
                )

            return explanation

        except Exception:

            logger.exception(
                "Scoring explanation failed"
            )

            return (
                "Unable to generate "
                "scoring explanation."
            )

    # =====================================================
    # ATTENTION EXPLANATION
    # =====================================================

    def explain_attention(
        self,
        attention_scores: Dict[str, float]
    ) -> str:

        try:

            if not attention_scores:

                return (
                    "Attention map data "
                    "was unavailable."
                )

            sorted_attention = sorted(
                attention_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )

            gate_name = (
                sorted_attention[0][0]
            )

            gate_score = (
                sorted_attention[0][1]
            )

            return (
                f"The highest attention "
                f"was observed in "
                f"'{gate_name}' "
                f"with a score of "
                f"{gate_score:.4f}."
            )

        except Exception:

            logger.exception(
                "Attention explanation failed"
            )

            return (
                "Unable to explain "
                "attention behavior."
            )

    # =====================================================
    # STUDENT EXPLANATION
    # =====================================================

    def generate_student_explanation(
        self,
        score: float,
        grade: str,
        feedback: List[str],
        verification_data=None
    ) -> str:

        try:

            text = (
                f"You achieved a score "
                f"of {score:.2f} "
                f"with grade {grade}. "
            )

            if feedback:

                text += (
                    "Key feedback points: "
                )

                text += " ".join(
                    feedback
                )

                text += " "

            if verification_data:

                text += (
                    self.explain_verification(
                        verification_data
                    )
                )

            return text

        except Exception:

            logger.exception(
                "Student explanation failed"
            )

            return (
                "Unable to generate "
                "student explanation."
            )

    # =====================================================
    # INSTRUCTOR EXPLANATION
    # =====================================================

    def generate_instructor_explanation(
        self,
        score: float,
        grade: str,
        confidence_score: float,
        attribution_scores: Dict,
        verification_data=None,
        scoring_breakdown=None
    ) -> str:

        try:

            explanation = (
                f"Assessment score: "
                f"{score:.2f}. "
                f"Grade: {grade}. "
                f"Confidence: "
                f"{confidence_score:.4f}. "
            )

            if verification_data:

                explanation += (
                    self.explain_verification(
                        verification_data
                    )
                )

                explanation += " "

            explanation += (
                self.explain_attribution(
                    attribution_scores
                )
            )

            if scoring_breakdown:

                explanation += " "

                explanation += (
                    self.explain_scoring(
                        score,
                        grade,
                        scoring_breakdown
                    )
                )

            return explanation

        except Exception:

            logger.exception(
                "Instructor explanation failed"
            )

            return (
                "Unable to generate "
                "instructor explanation."
            )

    # =====================================================
    # CONFIDENCE SUMMARY
    # =====================================================

    def generate_confidence_summary(
        self,
        attribution_map: np.ndarray
    ) -> Dict:

        try:

            confidence_score = (
                ConfidenceEstimator
                .explanation_confidence(
                    attribution_map
                )
            )

            confidence_level = (
                ConfidenceEstimator
                .confidence_level(
                    confidence_score
                )
            )

            return {
                "confidence_score":
                confidence_score,

                "confidence_level":
                confidence_level
            }

        except Exception:

            logger.exception(
                "Confidence summary failed"
            )

            return {
                "confidence_score": 0.0,
                "confidence_level": "Unknown"
            }

    # =====================================================
    # FULL PIPELINE EXPLANATION
    # =====================================================

    def generate_full_explanation(
        self,
        submission_id: str,
        score: float,
        grade: str,
        feedback: List[str],
        attribution_scores: Dict,
        verification_data=None,
        scoring_breakdown=None,
        confidence_score: float = 0.0
    ) -> Dict:

        try:

            student_explanation = (
                self.generate_student_explanation(
                    score=score,
                    grade=grade,
                    feedback=feedback,
                    verification_data=
                    verification_data
                )
            )

            instructor_explanation = (
                self.generate_instructor_explanation(
                    score=score,
                    grade=grade,
                    confidence_score=
                    confidence_score,
                    attribution_scores=
                    attribution_scores,
                    verification_data=
                    verification_data,
                    scoring_breakdown=
                    scoring_breakdown
                )
            )

            generated_at = (
                datetime.utcnow()
                .isoformat()
            )

            return {
                "submission_id":
                submission_id,

                "student_explanation":
                student_explanation,

                "instructor_explanation":
                instructor_explanation,

                "confidence_score":
                confidence_score,

                "attribution_scores":
                attribution_scores,

                "generated_at":
                generated_at
            }

        except Exception as e:

            logger.exception(
                "Full explanation generation failed"
            )

            raise e

    # =====================================================
    # ATTRIBUTION ANALYSIS
    # =====================================================

    def attribution_summary(
        self,
        attribution_map
    ):

        try:

            return (
                AttributionEngine
                .build_explanation_summary(
                    attribution_map
                )
            )

        except Exception:

            logger.exception(
                "Attribution summary failed"
            )

            return {}