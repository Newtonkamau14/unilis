import cv2
import numpy as np
import torch

from pathlib import Path
from typing import Dict
from typing import List

from config import settings
from logger import logger


class AttentionVisualizer:
    """
    Generates visual explanations
    from Attention U-Net attention maps.

    Features:
    - Normalize attention maps
    - Heatmap generation
    - Overlay creation
    - Multi-scale attention fusion
    - Save outputs
    """

    def __init__(self):

        pass

    @staticmethod
    def normalize_attention(
        attention_map
    ):

        attention_map = (
            attention_map.astype(
                np.float32
            )
        )

        attention_map = (
            attention_map
            - attention_map.min()
        ) / (
            attention_map.max()
            - attention_map.min()
            + 1e-8
        )

        return attention_map

    @staticmethod
    def tensor_to_map(
        attention_tensor: torch.Tensor
    ):

        attention = (
            attention_tensor
            .detach()
            .cpu()
            .numpy()
        )

        while attention.ndim > 2:

            attention = np.mean(
                attention,
                axis=0
            )

        return (
            AttentionVisualizer
            .normalize_attention(
                attention
            )
        )

    @staticmethod
    def resize_attention(
        attention_map,
        target_shape
    ):

        return cv2.resize(
            attention_map,
            (
                target_shape[1],
                target_shape[0]
            ),
            interpolation=cv2.INTER_LINEAR
        )

    @staticmethod
    def generate_heatmap(
        attention_map
    ):

        heatmap = cv2.applyColorMap(
            np.uint8(
                attention_map * 255
            ),
            cv2.COLORMAP_JET
        )

        return heatmap

    @staticmethod
    def overlay(
        image,
        heatmap,
        alpha=0.45
    ):

        return cv2.addWeighted(
            image,
            1 - alpha,
            heatmap,
            alpha,
            0
        )

    @staticmethod
    def save_image(
        image,
        output_path
    ):

        Path(
            output_path
        ).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cv2.imwrite(
            output_path,
            image
        )

        return output_path

    def visualize_single_gate(
        self,
        image,
        attention_tensor,
        gate_name
    ):

        try:

            h, w = image.shape[:2]

            attention_map = (
                self.tensor_to_map(
                    attention_tensor
                )
            )

            attention_map = (
                self.resize_attention(
                    attention_map,
                    (h, w)
                )
            )

            heatmap = (
                self.generate_heatmap(
                    attention_map
                )
            )

            overlay = (
                self.overlay(
                    image,
                    heatmap
                )
            )

            heatmap_path = (
                f"{settings.ATTENTION_DIR}/"
                f"{gate_name}_heatmap.jpg"
            )

            overlay_path = (
                f"{settings.ATTENTION_DIR}/"
                f"{gate_name}_overlay.jpg"
            )

            self.save_image(
                heatmap,
                heatmap_path
            )

            self.save_image(
                overlay,
                overlay_path
            )

            return {
                "gate": gate_name,
                "heatmap_path": heatmap_path,
                "overlay_path": overlay_path
            }

        except Exception as e:

            logger.exception(
                "Attention visualization failed"
            )

            raise e

    def visualize_all_gates(
        self,
        image,
        attention_maps: Dict[
            str,
            torch.Tensor
        ]
    ):

        outputs = []

        for (
            gate_name,
            attention_tensor
        ) in attention_maps.items():

            try:

                result = (
                    self.visualize_single_gate(
                        image,
                        attention_tensor,
                        gate_name
                    )
                )

                outputs.append(
                    result
                )

            except Exception:

                logger.exception(
                    f"Failed gate: "
                    f"{gate_name}"
                )

        return outputs

    def fuse_attention_maps(
        self,
        attention_maps: Dict[
            str,
            torch.Tensor
        ],
        target_shape
    ):

        fused = None

        for attention in (
            attention_maps.values()
        ):

            attention_map = (
                self.tensor_to_map(
                    attention
                )
            )

            attention_map = (
                self.resize_attention(
                    attention_map,
                    target_shape
                )
            )

            if fused is None:

                fused = attention_map

            else:

                fused += attention_map

        fused /= (
            len(attention_maps)
            + 1e-8
        )

        fused = (
            self.normalize_attention(
                fused
            )
        )

        return fused

    def generate_global_attention(
        self,
        image,
        attention_maps
    ):

        h, w = image.shape[:2]

        fused_attention = (
            self.fuse_attention_maps(
                attention_maps,
                (h, w)
            )
        )

        heatmap = (
            self.generate_heatmap(
                fused_attention
            )
        )

        overlay = (
            self.overlay(
                image,
                heatmap
            )
        )

        heatmap_path = (
            f"{settings.ATTENTION_DIR}/"
            f"global_attention_heatmap.jpg"
        )

        overlay_path = (
            f"{settings.ATTENTION_DIR}/"
            f"global_attention_overlay.jpg"
        )

        self.save_image(
            heatmap,
            heatmap_path
        )

        self.save_image(
            overlay,
            overlay_path
        )

        return {
            "heatmap_path": heatmap_path,
            "overlay_path": overlay_path
        }