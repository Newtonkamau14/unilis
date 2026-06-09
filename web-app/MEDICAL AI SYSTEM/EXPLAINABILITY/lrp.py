import torch

from logger import logger


class LayerwiseRelevancePropagation:

    def __init__(
        self,
        model
    ):
        self.model = model

    def explain(
        self,
        input_tensor,
        target_class
    ):

        try:

            self.model.eval()

            input_tensor.requires_grad_(
                True
            )

            output = self.model(
                input_tensor
            )

            if isinstance(
                output,
                (list, tuple)
            ):
                output = output[0]

            score = output[
                :,
                target_class
            ]

            self.model.zero_grad()

            score.backward()

            relevance = (
                input_tensor.grad
                .detach()
                .abs()
            )

            relevance = (
                relevance
                .sum(dim=1)
                .squeeze()
                .cpu()
                .numpy()
            )

            relevance = (
                relevance
                - relevance.min()
            ) / (
                relevance.max()
                - relevance.min()
                + 1e-8
            )

            return relevance

        except Exception as e:

            logger.exception(
                "LRP failed"
            )

            raise e