from __future__ import annotations


class FeedbackGenerator:

    def generate_short_answer_feedback(
        self,
        final_score: float,
        terminology_score: float,
        semantic_score: float,
        missing_terms: list[str],
    ) -> str:
        lines = []
        grade = self._grade_label(final_score)
        lines.append(f"Overall Score: {round(final_score * 100, 1)}% ({grade})")
        lines.append("")

        # Semantic feedback
        if semantic_score >= 0.85:
            lines.append("✓ Your answer demonstrates a strong understanding of the concept.")
        elif semantic_score >= 0.65:
            lines.append("~ Your answer captures some key ideas but could be more complete.")
        else:
            lines.append("✗ Your answer does not sufficiently address the question.")

        # Terminology feedback
        if terminology_score >= 0.85:
            lines.append("✓ Good use of domain-specific terminology.")
        elif terminology_score >= 0.55:
            lines.append("~ Some key terms were present but others were missing.")
        else:
            lines.append("✗ Consider using more precise technical vocabulary in your answer.")

        # Missing terms
        if missing_terms:
            terms_list = ", ".join(missing_terms[:5])  # cap at 5 to avoid clutter
            lines.append(f"\nKey terms to review: {terms_list}")

        return "\n".join(lines)

    def generate_mcq_feedback(
        self,
        is_correct: bool,
        selected_option: str,
        correct_option: str,
    ) -> str:
        if is_correct:
            return f"✓ Correct! You selected: {selected_option}"
        else:
            return (
                f"✗ Incorrect. You selected: {selected_option}\n"
                f"The correct answer was: {correct_option}"
            )

    @staticmethod
    def _grade_label(score: float) -> str:
        if score >= 0.90:
            return "Excellent"
        elif score >= 0.75:
            return "Good"
        elif score >= 0.55:
            return "Satisfactory"
        elif score >= 0.40:
            return "Needs Improvement"
        else:
            return "Unsatisfactory"