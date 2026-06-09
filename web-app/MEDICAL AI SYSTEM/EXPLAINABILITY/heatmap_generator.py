import cv2
import numpy as np
from pathlib import Path
from typing import Optional

from config import settings
from logger import logger


class HeatmapGenerator:
    """
    Production-grade heatmap generation.

    Supports:
    - GradCAM
    - GradCAM++
    - Integrated Gradients
    - SHAP
    - LRP
    - Attention Maps
    - Segmentation Probability Maps
    """

    SUPPORTED_COLORMAPS = {
        "jet": cv2.COLORMAP_JET,
        "hot": cv2.COLORMAP_HOT,
        "bone": cv2.COLORMAP_BONE,
        "viridis": cv2.COLORMAP_VIRIDIS,
        "plasma": cv2.COLORMAP_PLASMA,
        "inferno": cv2.COLORMAP_INFERNO,
        "magma": cv2.COLORMAP_MAGMA,
    }

    @staticmethod
    def normalize(
        explanation_map: np.ndarray
    ) -> np.ndarray:

        explanation_map = explanation_map.astype(
            np.float32
        )

        min_val = np.min(
            explanation_map
        )

        max_val = np.max(
            explanation_map
        )

        return (
            explanation_map - min_val
        ) / (
            max_val - min_val + 1e-8
        )

    @staticmethod
    def resize(
        explanation_map: np.ndarray,
        width: int,
        height: int
    ) -> np.ndarray:

        return cv2.resize(
            explanation_map,
            (width, height),
            interpolation=cv2.INTER_LINEAR
        )

    @classmethod
    def generate(
        cls,
        explanation_map: np.ndarray,
        colormap: str = "jet"
    ) -> np.ndarray:

        try:

            explanation_map = (
                cls.normalize(
                    explanation_map
                )
            )

            explanation_map = np.uint8(
                explanation_map * 255
            )

            cmap = (
                cls.SUPPORTED_COLORMAPS.get(
                    colormap.lower(),
                    cv2.COLORMAP_JET
                )
            )

            heatmap = cv2.applyColorMap(
                explanation_map,
                cmap
            )

            return heatmap

        except Exception as e:

            logger.exception(
                "Heatmap generation failed"
            )

            raise e

    @classmethod
    def generate_from_image_size(
        cls,
        explanation_map,
        image_shape,
        colormap="jet"
    ):

        h, w = image_shape[:2]

        explanation_map = cls.resize(
            explanation_map,
            w,
            h
        )

        return cls.generate(
            explanation_map,
            colormap
        )

    @staticmethod
    def save(
        heatmap: np.ndarray,
        filename: str
    ) -> str:

        output_path = (
            Path(
                settings.HEATMAP_DIR
            )
            / filename
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cv2.imwrite(
            str(output_path),
            heatmap
        )

        logger.info(
            f"Heatmap saved: "
            f"{output_path}"
        )

        return str(
            output_path
        )

    @classmethod
    def create_and_save(
        cls,
        explanation_map,
        filename,
        image_shape=None,
        colormap="jet"
    ) -> str:

        if image_shape is not None:

            heatmap = (
                cls.generate_from_image_size(
                    explanation_map,
                    image_shape,
                    colormap
                )
            )

        else:

            heatmap = cls.generate(
                explanation_map,
                colormap
            )

        return cls.save(
            heatmap,
            filename
        )