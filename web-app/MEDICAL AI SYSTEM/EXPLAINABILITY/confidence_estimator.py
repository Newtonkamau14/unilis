import numpy as np
import torch

from logger import logger


class ConfidenceEstimator:
    """
    Unified confidence estimation for:

    - Classification
    - Detection
    - Segmentation
    - Assessment
    """

    @staticmethod
    def classification_confidence(
        logits: torch.Tensor
    ) -> float:

        probs = torch.softmax(
            logits,
            dim=1
        )

        confidence = (
            probs.max()
            .detach()
            .cpu()
            .item()
        )

        return float(
            confidence
        )

    @staticmethod
    def detection_confidence(
        confidences
    ) -> float:

        if len(confidences) == 0:
            return 0.0

        return float(
            np.mean(confidences)
        )

    @staticmethod
    def segmentation_confidence(
        probability_map
    ) -> float:

        return float(
            np.mean(
                probability_map
            )
        )

    @staticmethod
    def assessment_confidence(
        similarity_score,
        completeness_score,
        labeling_score
    ) -> float:

        confidence = (
            similarity_score * 0.50
            +
            completeness_score * 0.30
            +
            labeling_score * 0.20
        )

        return round(
            confidence,
            4
        )

    @staticmethod
    def explanation_confidence(
        attribution_map
    ):

        try:

            attribution_map = np.abs(
                attribution_map
            )

            confidence = float(
                attribution_map.mean()
            )

            confidence = min(
                max(
                    confidence,
                    0.0
                ),
                1.0
            )

            return confidence

        except Exception:

            logger.exception(
                "Confidence estimation failed"
            )

            return 0.0

    @staticmethod
    def confidence_level(
        score
    ):

        if score >= 0.90:
            return "Very High"

        if score >= 0.75:
            return "High"

        if score >= 0.60:
            return "Moderate"

        if score >= 0.40:
            return "Low"

        return "Very Low"