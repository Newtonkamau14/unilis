import cv2
import numpy as np
from pathlib import Path

from config import settings
from logger import logger


class OverlayGenerator:
    """
    Creates explanation overlays.

    Supports:
    - GradCAM overlays
    - SHAP overlays
    - Attention overlays
    - Segmentation overlays
    """

    @staticmethod
    def create_overlay(
        image: np.ndarray,
        heatmap: np.ndarray,
        alpha: float = 0.45
    ) -> np.ndarray:

        try:

            if image.shape[:2] != heatmap.shape[:2]:

                heatmap = cv2.resize(
                    heatmap,
                    (
                        image.shape[1],
                        image.shape[0]
                    )
                )

            overlay = cv2.addWeighted(
                image,
                1 - alpha,
                heatmap,
                alpha,
                0
            )

            return overlay

        except Exception as e:

            logger.exception(
                "Overlay generation failed"
            )

            raise e

    @staticmethod
    def create_segmentation_overlay(
        image,
        mask,
        color=(0, 255, 0),
        alpha=0.35
    ):

        overlay = image.copy()

        colored_mask = np.zeros_like(
            image
        )

        colored_mask[
            mask > 0
        ] = color

        overlay = cv2.addWeighted(
            image,
            1.0,
            colored_mask,
            alpha,
            0
        )

        return overlay

    @staticmethod
    def save(
        overlay,
        filename
    ):

        output_path = (
            Path(
                settings.OVERLAY_DIR
            )
            / filename
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cv2.imwrite(
            str(output_path),
            overlay
        )

        logger.info(
            f"Overlay saved: "
            f"{output_path}"
        )

        return str(
            output_path
        )

    @classmethod
    def create_and_save(
        cls,
        image,
        heatmap,
        filename,
        alpha=0.45
    ):

        overlay = cls.create_overlay(
            image,
            heatmap,
            alpha
        )

        return cls.save(
            overlay,
            filename
        )