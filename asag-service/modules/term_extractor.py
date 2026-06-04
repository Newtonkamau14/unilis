from __future__ import annotations

try:
    import spacy
    _nlp = None

    def _get_nlp():
        global _nlp
        if _nlp is None:
            try:
                _nlp = spacy.load("en_core_web_sm")
            except OSError:
                raise RuntimeError(
                    "spaCy model not found. Run: python -m spacy download en_core_web_sm"
                )
        return _nlp

    _SPACY_AVAILABLE = True
except ImportError:
    _SPACY_AVAILABLE = False


# POS tags to keep (Universal POS tagset used by spaCy)
KEEP_POS = {"NOUN", "PROPN", "VERB", "ADJ"}

# Fallback: suffixes that often indicate domain terms
DOMAIN_SUFFIXES = (
    "tion", "ism", "ity", "ment", "ence", "ance", "ogy", "sis",
    "ics", "ing", "ase", "ose", "ide", "ine"
)


def extract_terms(text: str, keyword_list: list[str] | None = None) -> list[str]:
    """
    Extract meaningful terms from text using POS tagging (spaCy) or fallback.

    Args:
        text:         The reference answer (stop-word-removed).
        keyword_list: Optional domain keyword list to always include.

    Returns:
        Deduplicated list of domain terms (lowercase).
    """
    terms = set()

    if _SPACY_AVAILABLE:
        nlp = _get_nlp()
        doc = nlp(text)
        for token in doc:
            if token.pos_ in KEEP_POS and not token.is_stop and len(token.text) > 2:
                terms.add(token.lemma_.lower())
    else:
        # Fallback: include words with domain-like suffixes or length > 5
        for word in text.lower().split():
            if len(word) > 5 or any(word.endswith(s) for s in DOMAIN_SUFFIXES):
                terms.add(word)

    # Always include explicit keyword list terms
    if keyword_list:
        for kw in keyword_list:
            terms.add(kw.lower().strip())

    return sorted(terms)