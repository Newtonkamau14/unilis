"""
preprocessor.py
---------------
Handles text cleaning before BERT encoding.
- Stop word removal applied to question_context + reference_answer
- Tokenizer applied to student_answer
"""

import re
import string

# Basic English stop words (extend or replace with nltk if available)
STOP_WORDS = {
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "for",
    "of", "and", "or", "but", "not", "with", "as", "by", "from",
    "that", "this", "was", "are", "be", "been", "being", "have",
    "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "what", "which",
    "who", "whom", "whose", "when", "where", "why", "how"
}


def remove_stop_words(text: str) -> str:
    """Remove stop words from text. Used for reference answer + context."""
    tokens = text.lower().split()
    filtered = [t.strip(string.punctuation) for t in tokens if t.lower() not in STOP_WORDS]
    return " ".join(filtered)


def tokenize(text: str) -> list[str]:
    """Basic whitespace + punctuation tokenizer for student answer."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # replace punctuation with space
    tokens = [t for t in text.split() if t]
    return tokens


def preprocess(question_context: str, reference_answer: str, student_answer: str) -> dict:
    """
    Full preprocessing pipeline.

    Returns:
        dict with keys:
            - cleaned_reference: stop-word-removed reference text
            - cleaned_context: stop-word-removed question context
            - student_tokens: tokenized student answer
            - raw_student: original student answer (preserved for sentence embeddings)
    """
    return {
        "cleaned_reference": remove_stop_words(reference_answer),
        "cleaned_context": remove_stop_words(question_context),
        "student_tokens": tokenize(student_answer),
        "raw_student": student_answer,
        "raw_reference": reference_answer,
    }