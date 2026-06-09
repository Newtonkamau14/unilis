import torch
import torch.nn as nn
from typing import Dict
from typing import List

from logger import logger


class AttentionGateExtractor:
    """
    Extracts Attention Gate outputs
    from Attention U-Net models.

    Supports:
    - Multiple attention gates
    - Deep supervision architectures
    - Medical image segmentation
    """

    def __init__(
        self,
        model: nn.Module
    ):
        self.model = model

        self.attention_maps = {}

        self.hooks = []

    def clear(self):

        self.attention_maps.clear()

    def remove_hooks(self):

        for hook in self.hooks:
            hook.remove()

        self.hooks.clear()

    def _save_attention(
        self,
        layer_name
    ):

        def hook(
            module,
            inputs,
            output
        ):

            try:

                if isinstance(
                    output,
                    tuple
                ):
                    output = output[0]

                self.attention_maps[
                    layer_name
                ] = output.detach()

            except Exception:

                logger.exception(
                    f"Failed extracting "
                    f"{layer_name}"
                )

        return hook

    def register_hooks(self):

        self.remove_hooks()

        for name, module in (
            self.model.named_modules()
        ):

            name_lower = name.lower()

            if (
                "attention" in name_lower
                or "gate" in name_lower
                or "attn" in name_lower
            ):

                logger.info(
                    f"Registering attention hook: "
                    f"{name}"
                )

                hook = (
                    module.register_forward_hook(
                        self._save_attention(
                            name
                        )
                    )
                )

                self.hooks.append(
                    hook
                )

    @torch.no_grad()
    def extract(
        self,
        image_tensor
    ) -> Dict[str, torch.Tensor]:

        try:

            self.clear()

            self.model.eval()

            _ = self.model(
                image_tensor
            )

            return {
                k: v.cpu()
                for k, v in self.attention_maps.items()
            }

        except Exception as e:

            logger.exception(
                "Attention extraction failed"
            )

            raise e

    def get_gate_names(
        self
    ) -> List[str]:

        return list(
            self.attention_maps.keys()
        )