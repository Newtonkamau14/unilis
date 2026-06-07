from __future__ import annotations
from typing import Literal


AggregationMode = Literal["gating", "semantic_only", "terminology_only", "weighted_sum"]


class ScoreAggregator:
    """
    Combines semantic and terminology scores using a gating/penalty approach
    to prevent double-counting the mathematical overlap between both scores.

    Args:
        mode:              Aggregation strategy (default: "gating").
        term_threshold:    Terminology coverage below this triggers a penalty (default 0.60).
        penalty_strength:  How severely missing terms reduce the semantic score (default 0.40).
        terminology_weight: Used only in "weighted_sum" mode (default 0.40).
        semantic_weight:    Used only in "weighted_sum" mode (default 0.60).
    """

    def __init__(
        self,
        mode: AggregationMode = "gating",
        term_threshold: float = 0.60,
        penalty_strength: float = 0.40,
        terminology_weight: float = 0.40,
        semantic_weight: float = 0.60,
    ):
        self.mode = mode
        self.term_threshold = term_threshold
        self.penalty_strength = penalty_strength
        self.terminology_weight = terminology_weight
        self.semantic_weight = semantic_weight

    def aggregate(
        self,
        terminology_score: float,
        semantic_score: float,
    ) -> dict:
        """
        Args:
            terminology_score: Float in [0, 1].
            semantic_score:    Float in [0, 1].

        Returns:
            dict with keys:
                final_score (float): The aggregated score in [0, 1].
                explanation (str):   Human-readable explanation of how score was computed.
                penalty_applied (float): Penalty deducted (0 if none).
        """
        if self.mode == "semantic_only":
            return {
                "final_score": round(semantic_score, 4),
                "explanation": "Score based on semantic understanding only (ablation mode).",
                "penalty_applied": 0.0,
            }

        elif self.mode == "terminology_only":
            return {
                "final_score": round(terminology_score, 4),
                "explanation": "Score based on terminology coverage only (ablation mode).",
                "penalty_applied": 0.0,
            }

        elif self.mode == "weighted_sum":
            # Original naive approach — kept for ablation comparison
            final = (
                self.terminology_weight * terminology_score
                + self.semantic_weight * semantic_score
            )
            return {
                "final_score": round(max(0.0, min(1.0, final)), 4),
                "explanation": (
                    f"Weighted sum: {self.semantic_weight}×semantic "
                    f"+ {self.terminology_weight}×terminology "
                    f"(naive baseline — may double-count overlap)."
                ),
                "penalty_applied": 0.0,
            }

        else:  # "gating" — recommended
            terminology_penalty = max(0.0, self.term_threshold - terminology_score)
            penalty_weight      = self.penalty_strength * terminology_penalty
            final               = semantic_score * (1.0 - penalty_weight)
            final               = round(max(0.0, min(1.0, final)), 4)
            penalty_applied     = round(semantic_score - final, 4)

            if terminology_penalty == 0.0:
                explanation = (
                    f"Semantic score: {semantic_score:.2f}. "
                    f"Terminology coverage sufficient ({terminology_score:.2f} ≥ {self.term_threshold}). "
                    f"No penalty applied."
                )
            else:
                explanation = (
                    f"Semantic score: {semantic_score:.2f}. "
                    f"Terminology gap: {terminology_score:.2f} < threshold {self.term_threshold}. "
                    f"Score reduced by {penalty_applied:.2f} due to missing domain terms. "
                    f"Final: {final:.2f}."
                )

            return {
                "final_score": final,
                "explanation": explanation,
                "penalty_applied": penalty_applied,
            }