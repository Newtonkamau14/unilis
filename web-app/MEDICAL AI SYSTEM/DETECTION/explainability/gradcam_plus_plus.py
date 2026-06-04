import torch
import torch.nn.functional as F

from logger import logger


class GradCAMPlusPlus:

    def __init__(
        self,
        model,
        target_layer
    ):
        self.model = model
        self.target_layer = target_layer

        self.activations = None
        self.gradients = None

        self._register_hooks()

    def _register_hooks(self):

        def forward_hook(
            module,
            inp,
            out
        ):
            self.activations = out

        def backward_hook(
            module,
            gin,
            gout
        ):
            self.gradients = gout[0]

        self.target_layer.register_forward_hook(
            forward_hook
        )

        self.target_layer.register_full_backward_hook(
            backward_hook
        )

    def generate(
        self,
        input_tensor,
        target_class=None
    ):

        try:

            output = self.model(
                input_tensor
            )

            if isinstance(
                output,
                (tuple, list)
            ):
                output = output[0]

            if target_class is None:

                target_class = (
                    output.argmax(
                        dim=1
                    )
                    .item()
                )

            score = output[
                :,
                target_class
            ]

            self.model.zero_grad()

            score.backward(
                retain_graph=True
            )

            gradients = self.gradients

            activations = (
                self.activations
            )

            grads_power_2 = (
                gradients ** 2
            )

            grads_power_3 = (
                gradients ** 3
            )

            denominator = (
                2
                * grads_power_2
                +
                torch.sum(
                    activations
                    * grads_power_3,
                    dim=(2, 3),
                    keepdim=True
                )
            )

            denominator = torch.where(
                denominator != 0,
                denominator,
                torch.ones_like(
                    denominator
                )
            )

            alpha = (
                grads_power_2
                / denominator
            )

            positive_gradients = (
                F.relu(
                    gradients
                )
            )

            weights = torch.sum(
                alpha
                *
                positive_gradients,
                dim=(2, 3),
                keepdim=True
            )

            cam = torch.sum(
                weights
                * activations,
                dim=1
            )

            cam = F.relu(cam)

            cam = (
                cam - cam.min()
            ) / (
                cam.max()
                - cam.min()
                + 1e-8
            )

            return (
                cam.squeeze()
                .cpu()
                .detach()
                .numpy()
            )

        except Exception as e:

            logger.exception(
                "GradCAM++ failed"
            )

            raise e