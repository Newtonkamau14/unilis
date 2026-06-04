"""
mcq_grader.py
--------------
Handles Multiple Choice Question grading.

Why MCQ is a separate pipeline:
  - No token/sentence embeddings are needed.
  - Missing Terms Report is NOT generated (irrelevant for MCQ).
  - Score is binary (correct/incorrect) — no weighted aggregation.
  - Student answer is matched against the correct option by exact or
    near-exact string comparison (handles "A", "A.", "Option A", full text).

This answers the lecturer's concern: the system routes based on
QuestionType BEFORE any NLP processing, so MCQ questions never
go through the BERT encoder pipeline at all.
"""

from __future__ import annotations
import re


def _normalize(text: str) -> str:
    """Strip leading option labels like 'A.', 'B)', '(C)' and lowercase."""
    text = text.strip().lower()
    text = re.sub(r"^[\(\[]?[a-d][\)\].]?\s*", "", text)  # remove option letter prefix
    return text.strip()


def _extract_option_letter(text: str) -> str | None:
    """Extract just the letter from answers like 'A', 'B.', '(C)'."""
    match = re.match(r"^[\(\[]?([a-dA-D])[\)\].]?$", text.strip())
    return match.group(1).upper() if match else None


class MCQGrader:
    """
    Grades a multiple choice answer.

    Matching strategy (in priority order):
      1. Letter match — student answers "B" and correct is "B. photosynthesis"
      2. Full text match — student writes out the full option text
      3. Normalized text match — ignoring option labels and case
    """

    def grade(
        self,
        student_answer: str,
        reference_answer: str,
        mcq_options: list[str] | None = None,
    ) -> dict:
        """
        Args:
            student_answer:  What the student selected/wrote.
            reference_answer: The correct answer (can be letter or full text).
            mcq_options:     Full list of options, e.g. ["A. ...", "B. ..."].

        Returns:
            dict with: is_correct, selected_option, correct_option, score
        """
        student_norm = _normalize(student_answer)
        reference_norm = _normalize(reference_answer)

        student_letter = _extract_option_letter(student_answer)
        reference_letter = _extract_option_letter(reference_answer)

        # Strategy 1: Both are single letters
        if student_letter and reference_letter:
            is_correct = student_letter == reference_letter
        # Strategy 2 & 3: Normalized text comparison
        else:
            is_correct = student_norm == reference_norm

        # If still unresolved and options list available, resolve by position
        if not is_correct and mcq_options and student_letter:
            option_map = {}
            for opt in mcq_options:
                letter = _extract_option_letter(opt.split(".")[0])
                if letter:
                    option_map[letter] = _normalize(opt)
            student_resolved = option_map.get(student_letter, student_norm)
            is_correct = student_resolved == reference_norm

        return {
            "is_correct": is_correct,
            "selected_option": student_answer.strip(),
            "correct_option": reference_answer.strip(),
            "score": 1.0 if is_correct else 0.0,
        }