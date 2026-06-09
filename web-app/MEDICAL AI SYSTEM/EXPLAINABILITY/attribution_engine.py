import numpy as np
from typing import Dict
from typing import List

from logger import logger


class AttributionEngine:
    """
    Produces attribution statistics
    for explainability reports.

    Used by:
    - GradCAM
    - GradCAM++
    - SHAP
    - LRP
    - Attention U-Net
    """

    @staticmethod
    def calculate_region_importance(
        attribution_map: np.ndarray
    ) -> Dict[str, float]:

        h, w = attribution_map.shape

        top = attribution_map[
            : h // 2,
            :
        ]

        bottom = attribution_map[
            h // 2 :,
            :
        ]

        left = attribution_map[
            :,
            : w // 2
        ]

        right = attribution_map[
            :,
            w // 2 :
        ]

        scores = {
            "top_region":
            float(np.mean(top)),

            "bottom_region":
            float(np.mean(bottom)),

            "left_region":
            float(np.mean(left)),

            "right_region":
            float(np.mean(right))
        }

        total = sum(
            scores.values()
        ) + 1e-8

        return {
            k: round(
                v / total,
                4
            )
            for k, v
            in scores.items()
        }

    @staticmethod
    def calculate_intensity_statistics(
        attribution_map
    ):

        return {
            "mean":
            float(
                np.mean(
                    attribution_map
                )
            ),

            "std":
            float(
                np.std(
                    attribution_map
                )
            ),

            "max":
            float(
                np.max(
                    attribution_map
                )
            ),

            "min":
            float(
                np.min(
                    attribution_map
                )
            ),
        }

    @staticmethod
    def top_k_regions(
        attribution_map,
        k=10
    ):

        flat = attribution_map.flatten()

        indices = np.argsort(
            flat
        )[::-1][:k]

        scores = flat[
            indices
        ]

        output = []

        for idx, score in zip(
            indices,
            scores
        ):

            output.append({
                "pixel":
                int(idx),

                "importance":
                float(score)
            })

        return output

    @staticmethod
    def segmentation_attribution(
        segmentation_mask
    ):

        unique = np.unique(
            segmentation_mask
        )

        results = {}

        total_pixels = (
            segmentation_mask.size
        )

        for cls in unique:

            pixels = np.sum(
                segmentation_mask == cls
            )

            results[
                str(cls)
            ] = round(
                pixels
                /
                total_pixels,
                4
            )

        return results

    @staticmethod
    def attention_attribution(
        attention_maps
    ):

        results = {}

        for (
            gate_name,
            attention_map
        ) in attention_maps.items():

            try:

                score = float(
                    np.mean(
                        attention_map
                    )
                )

                results[
                    gate_name
                ] = round(
                    score,
                    4
                )

            except Exception:

                logger.exception(
                    f"Failed gate "
                    f"{gate_name}"
                )

        total = (
            sum(
                results.values()
            )
            + 1e-8
        )

        normalized = {
            k: round(
                v / total,
                4
            )
            for k, v
            in results.items()
        }

        return normalized

    @staticmethod
    def build_explanation_summary(
        attribution_map
    ):

        stats = (
            AttributionEngine
            .calculate_intensity_statistics(
                attribution_map
            )
        )

        region_scores = (
            AttributionEngine
            .calculate_region_importance(
                attribution_map
            )
        )

        return {
            "statistics":
            stats,

            "regions":
            region_scores,

            "top_regions":
            AttributionEngine
            .top_k_regions(
                attribution_map,
                10
            )
        }