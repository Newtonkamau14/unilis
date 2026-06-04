from captum.attr import (
    IntegratedGradients
)

from logger import logger


class IntegratedGradientsExplainer:

    def __init__(
        self,
        model
    ):
        self.model = model

        self.ig = (
            IntegratedGradients(
                self.model
            )
        )

    def explain(
        self,
        input_tensor,
        target_class
    ):

        try:

            attributions = (
                self.ig.attribute(
                    input_tensor,
                    target=target_class,
                    n_steps=50
                )
            )

            attribution_map = (
                attributions
                .sum(dim=1)
                .squeeze()
                .cpu()
                .detach()
                .numpy()
            )

            return attribution_map

        except Exception as e:

            logger.exception(
                "Integrated Gradients failed"
            )

            raise e