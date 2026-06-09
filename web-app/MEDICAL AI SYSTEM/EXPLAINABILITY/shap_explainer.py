import numpy as np
import shap
import torch

from logger import logger


class SHAPExplainer:

    def __init__(
        self,
        model
    ):
        self.model = model

    def explain(
        self,
        input_tensor,
        background_samples=10
    ):

        try:

            self.model.eval()

            background = torch.zeros(
                (
                    background_samples,
                    *input_tensor.shape[1:]
                ),
                device=input_tensor.device
            )

            explainer = (
                shap.DeepExplainer(
                    self.model,
                    background
                )
            )

            shap_values = (
                explainer.shap_values(
                    input_tensor
                )
            )

            if isinstance(
                shap_values,
                list
            ):
                shap_values = (
                    shap_values[0]
                )

            shap_map = np.mean(
                np.abs(
                    shap_values
                ),
                axis=1
            )

            shap_map = (
                shap_map.squeeze()
            )

            shap_map = (
                shap_map
                - shap_map.min()
            ) / (
                shap_map.max()
                - shap_map.min()
                + 1e-8
            )

            return shap_map

        except Exception as e:

            logger.exception(
                "SHAP failed"
            )

            raise e