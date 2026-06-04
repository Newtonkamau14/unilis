"""
semantic_scorer.py
-------------------
Uses sentence-level BERT embeddings (CLS pooling) to measure
the overall meaning similarity between the student and reference answers.

Unlike TerminologyScorer which works term-by-term, this scorer treats each
answer as a single semantic unit. A student who says "plants produce energy
from sunlight" scores high even if they never use the word "photosynthesis".
"""

from __future__ import annotations
import numpy as np
from .bert_encoder import BERTEncoder


class SemanticScorer:
    """
    Measures semantic similarity between student answer and reference answer
    using cosine similarity of sentence embeddings.
    """

    def __init__(self, encoder: BERTEncoder):
        self.encoder = encoder

    def score(self, reference_answer: str, student_answer: str) -> dict:
        """
        Args:
            reference_answer: Full reference/model answer text.
            student_answer:   Full student answer text.

        Returns:
            dict with keys: score (float 0-1), similarity_explanation (str)
        """
        ref_vec = self.encoder.get_sentence_embedding(reference_answer)
        stu_vec = self.encoder.get_sentence_embedding(student_answer)

        # Cosine similarity (normalized vectors → dot product = cosine)
        similarity = float(np.dot(ref_vec, stu_vec))
        similarity = max(0.0, min(1.0, similarity))  # clamp to [0, 1]

        explanation = self._explain(similarity)

        return {
            "score": round(similarity, 4),
            "similarity_explanation": explanation,
        }

    @staticmethod
    def _explain(score: float) -> str:
        if score >= 0.90:
            return "Excellent semantic match — answer meaning closely aligns with the reference."
        elif score >= 0.75:
            return "Good semantic match — most key ideas are present."
        elif score >= 0.55:
            return "Partial semantic match — some relevant ideas present but answer is incomplete."
        elif score >= 0.35:
            return "Weak semantic match — answer touches on the topic but misses core meaning."
        else:
            return "Poor semantic match — answer does not align with the expected meaning."