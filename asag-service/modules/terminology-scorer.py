from __future__ import annotations
import numpy as np
from .bert_encoder import BERTEncoder
from .term_extractor import extract_terms


SIMILARITY_THRESHOLD = 0.75  # cosine similarity cutoff to count a term as "matched"


class TerminologyScorer:
    """
    Scores how well a student answer covers domain-specific terminology
    drawn from the reference answer and keyword list.
    """

    def __init__(self, encoder: BERTEncoder):
        self.encoder = encoder

    def score(
        self,
        reference_terms: list[str],
        student_tokens: list[str],
    ) -> dict:
        """
        Args:
            reference_terms: Key terms extracted from the reference answer
                             (already POS-tagged nouns/verbs/adjectives).
            student_tokens:  Raw tokens from the student's answer.

        Returns:
            dict with keys: score (float), matched_terms, missing_terms
        """
        if not reference_terms:
            return {"score": 1.0, "matched_terms": [], "missing_terms": []}

        # Embed reference terms and student tokens
        ref_embeddings = self.encoder.get_token_embeddings(reference_terms)
        stu_embeddings = self.encoder.get_token_embeddings(student_tokens)

        matched = []
        missing = []

        for term, ref_vec in ref_embeddings.items():
            best_similarity = 0.0
            for stu_vec in stu_embeddings.values():
                # Cosine similarity (vectors are already L2-normalized)
                sim = float(np.dot(ref_vec, stu_vec))
                if sim > best_similarity:
                    best_similarity = sim

            if best_similarity >= SIMILARITY_THRESHOLD:
                matched.append(term)
            else:
                missing.append(term)

        score = len(matched) / len(reference_terms) if reference_terms else 1.0

        return {
            "score": round(score, 4),
            "matched_terms": matched,
            "missing_terms": missing,
        }