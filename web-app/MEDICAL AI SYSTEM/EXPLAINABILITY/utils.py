import os
import uuid
from pathlib import Path

import cv2
import numpy as np
import torch

from config import settings


# =====================================================
# FILES
# =====================================================

def generate_id() -> str:

    return str(uuid.uuid4())


def ensure_directory(
    directory: str
):

    Path(directory).mkdir(
        parents=True,
        exist_ok=True
    )


# =====================================================
# IMAGE LOADING
# =====================================================

def load_image(
    image_path: str
):

    image = cv2.imread(
        image_path
    )

    if image is None:

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    return image


def save_image(
    image,
    output_path
):

    ensure_directory(
        os.path.dirname(output_path)
    )

    cv2.imwrite(
        output_path,
        image
    )

    return output_path


# =====================================================
# NORMALIZATION
# =====================================================

def normalize_heatmap(
    heatmap
):

    heatmap = heatmap.astype(
        np.float32
    )

    heatmap = (
        heatmap - heatmap.min()
    ) / (
        heatmap.max()
        - heatmap.min()
        + 1e-8
    )

    return heatmap


# =====================================================
# DEVICE
# =====================================================

def get_device():

    if settings.DEVICE == "cuda":

        if torch.cuda.is_available():

            return torch.device(
                "cuda"
            )

    return torch.device(
        "cpu"
    )


# =====================================================
# TENSOR CONVERSION
# =====================================================

def image_to_tensor(
    image
):

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image = cv2.resize(
        image,
        (
            settings.DEFAULT_IMAGE_SIZE,
            settings.DEFAULT_IMAGE_SIZE
        )
    )

    image = image.astype(
        np.float32
    ) / 255.0

    image = np.transpose(
        image,
        (2, 0, 1)
    )

    tensor = torch.tensor(
        image
    ).unsqueeze(0)

    return tensor


# =====================================================
# CONFIDENCE
# =====================================================

def confidence_from_logits(
    logits
):

    probabilities = torch.softmax(
        logits,
        dim=1
    )

    confidence = (
        probabilities.max()
        .detach()
        .cpu()
        .item()
    )

    return float(confidence)


# =====================================================
# FILE NAMES
# =====================================================

def build_output_filename(
    prefix: str,
    extension: str
):

    return (
        f"{prefix}_"
        f"{generate_id()}."
        f"{extension}"
    )