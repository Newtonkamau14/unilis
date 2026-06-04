
from __future__ import annotations
from functools import lru_cache
from typing import Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False


DEFAULT_MODEL = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_model(model_name: str) -> "SentenceTransformer":
    if not _ST_AVAILABLE:
        raise RuntimeError(
            "sentence-transformers is not installed. "
            "Run: pip install sentence-transformers"
        )
    return SentenceTransformer(model_name)


class BERTEncoder:
    """
    Encodes text into token and sentence embeddings.

    Attributes:
        model_name (str): HuggingFace model identifier.
    """

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self._model: Optional["SentenceTransformer"] = None

    def _get_model(self) -> "SentenceTransformer":
        if self._model is None:
            self._model = _load_model(self.model_name)
        return self._model

    def get_sentence_embedding(self, text: str) -> np.ndarray:
        """
        Returns a single pooled sentence vector (1D array).
        Used by SemanticScorer for cosine similarity.
        """
        model = self._get_model()
        embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding  # shape: (embedding_dim,)

    def get_token_embeddings(self, tokens: list[str]) -> dict[str, np.ndarray]:
        """
        Returns a mapping of token → embedding vector.
        Used by TerminologyScorer to compare individual term representations.

        Args:
            tokens: List of individual word/term strings.

        Returns:
            dict mapping each token to its embedding array.
        """
        if not tokens:
            return {}
        model = self._get_model()
        embeddings = model.encode(tokens, convert_to_numpy=True, normalize_embeddings=True)
        return {token: emb for token, emb in zip(tokens, embeddings)}