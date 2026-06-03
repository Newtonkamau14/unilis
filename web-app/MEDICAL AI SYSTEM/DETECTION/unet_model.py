import os
import torch
import numpy as np

from PIL import Image
from monai.networks.nets import AttentionUnet
from torchvision import transforms


# =====================================================
# CONFIGURATION
# =====================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

MODEL_PATH = "weights/attention_unet.pth"

IMAGE_SIZE = (512, 512)

THRESHOLD = 0.5


# =====================================================
# IMAGE PREPROCESSING
# =====================================================

transform = transforms.Compose([
    transforms.Resize(IMAGE_SIZE),
    transforms.ToTensor()
])


# =====================================================
# MODEL INITIALIZATION
# =====================================================

def load_model():

    model = AttentionUnet(
        spatial_dims=2,
        in_channels=3,
        out_channels=1,
        channels=(64, 128, 256, 512),
        strides=(2, 2, 2)
    ).to(DEVICE)

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model weights not found: {MODEL_PATH}"
        )

    model.load_state_dict(
        torch.load(
            "weights/attention_unet.pth",
        map_location=DEVICE
        )
    )

    model.eval()

    return model


# Load once during service startup
model = load_model()


# =====================================================
# INTERNAL INFERENCE
# =====================================================

def _predict_mask(image_path: str):

    image = Image.open(image_path).convert("RGB")

    tensor = transform(image)

    tensor = tensor.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        prediction = model(tensor)

    mask = torch.sigmoid(prediction)

    mask = mask.squeeze().cpu().numpy()

    binary_mask = (
        mask > THRESHOLD
    ).astype(np.uint8)

    return binary_mask


# =====================================================
# RETURN MASK AS NUMPY ARRAY
# =====================================================

def segment(image_path: str):

    """
    Returns segmentation mask as numpy array.
    """

    return _predict_mask(image_path)


# =====================================================
# SAVE MASK TO FILE
# =====================================================

def segment_and_save(
    image_path: str,
    output_path: str
):

    """
    Generates segmentation mask
    and saves it as PNG.
    """

    mask = _predict_mask(image_path)

    mask_image = (
        mask * 255
    ).astype(np.uint8)

    Image.fromarray(mask_image).save(
        output_path
    )

    return output_path


# =====================================================
# OPTIONAL OVERLAY VISUALIZATION
# =====================================================

def create_overlay(
    image_path: str,
    output_path: str
):

    """
    Creates image + segmentation overlay.
    Useful for explainability.
    """

    original = Image.open(
        image_path
    ).convert("RGB")

    original = original.resize(
        IMAGE_SIZE
    )

    mask = _predict_mask(
        image_path
    )

    mask_rgb = np.zeros(
        (mask.shape[0], mask.shape[1], 3),
        dtype=np.uint8
    )

    # Red overlay
    mask_rgb[:, :, 0] = mask * 255

    overlay = (
        0.7 * np.array(original)
        + 0.3 * mask_rgb
    ).astype(np.uint8)

    Image.fromarray(
        overlay
    ).save(output_path)

    return output_path