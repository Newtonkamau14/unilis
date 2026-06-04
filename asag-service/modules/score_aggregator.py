"""
score_aggregator.py
--------------------
Combines TerminologyScore and SemanticScore into a single weighted score.

Weights are configurable. Default: 40% terminology, 60% semantic.
The lecturer's concern about terminology relevance is addressed here:
  - For SHORT_ANSWER: both scores are used.
  - For MCQ: aggregator is bypassed entirely (see grader.py).

Rationale for default weights:
  - Semantic understanding is more important than exact vocabulary in most
    educational contexts. A student who demonstrates understanding but uses
    informal language should not be penalized heavily.
  - Terminology weight can be increased for technical/professional courses.
"""

from __future__ import annotations


DEFAULT_WEIGHTS = {
    "terminology": 0.40,
    "semantic": 0.60,
}


class ScoreAggregator:
    """
    Computes a final weighted score from component scores.

    Args:
        terminology_weight: Weight for terminology score (default 0.4).
        semantic_weight:    Weight for semantic score (default 0.6).
    """

    def __init__(
        self,
        terminology_weight: float = DEFAULT_WEIGHTS["terminology"],
        semantic_weight: float = DEFAULT_WEIGHTS["semantic"],
    ):
        total = terminology_weight + semantic_weight
        if abs(total - 1.0) > 0.001:
            raise ValueError(
                f"Weights must sum to 1.0, got {total}. "
                "Adjust terminology_weight and semantic_weight."
            )
        self.terminology_weight = terminology_weight
        self.semantic_weight = semantic_weight

    def aggregate(
        self,
        terminology_score: float,
        semantic_score: float,
    ) -> float:
        """
        Args:
            terminology_score: Float in [0, 1].
            semantic_score:    Float in [0, 1].

        Returns:
            Weighted final score as float in [0, 1].
        """
        final = (
            self.terminology_weight * terminology_score
            + self.semantic_weight * semantic_score
        )
        return round(max(0.0, min(1.0, final)), 4)