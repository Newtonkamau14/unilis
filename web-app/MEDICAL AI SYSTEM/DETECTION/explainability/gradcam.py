import torch
import torch.nn.functional as F
import numpy as np

from logger import logger


class GradCAM:

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
            inputs,
            output
        ):
            self.activations = output.detach()

        def backward_hook(
            module,
            grad_input,
            grad_output
        ):
            self.gradients = grad_output[0].detach()

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

            self.model.eval()

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
                    torch.argmax(
                        output,
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

            gradients = (
                self.gradients
            )

            activations = (
                self.activations
            )

            weights = torch.mean(
                gradients,
                dim=(2, 3),
                keepdim=True
            )

            cam = torch.sum(
                weights * activations,
                dim=1
            )

            cam = F.relu(cam)

            cam = (
                cam -
                cam.min()
            ) / (
                cam.max()
                -
                cam.min()
                +
                1e-8
            )

            return (
                cam
                .squeeze()
                .cpu()
                .numpy()
            )

        except Exception as e:

            logger.exception(
                "GradCAM failed"
            )

            raise e