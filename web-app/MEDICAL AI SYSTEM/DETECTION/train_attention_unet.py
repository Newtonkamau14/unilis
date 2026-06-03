import os
import copy
import numpy as np

from PIL import Image
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

from torchvision import transforms

from monai.networks.nets import AttentionUnet
from monai.losses import DiceLoss


# =====================================================
# CONFIGURATION
# =====================================================

TRAIN_IMAGES = "datasets/anatomy_segmentation/train/images"
TRAIN_MASKS = "datasets/anatomy_segmentation/train/masks"

VAL_IMAGES = "datasets/anatomy_segmentation/val/images"
VAL_MASKS = "datasets/anatomy_segmentation/val/masks"

MODEL_OUTPUT = "weights/attention_unet.pth"

IMAGE_SIZE = (512, 512)

BATCH_SIZE = 4

EPOCHS = 50

LEARNING_RATE = 1e-4


DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# =====================================================
# DATASET
# =====================================================

class AnatomyDataset(Dataset):

    def __init__(
        self,
        image_dir,
        mask_dir
    ):

        self.image_dir = image_dir
        self.mask_dir = mask_dir

        self.images = sorted(
            os.listdir(image_dir)
        )

        self.transform = transforms.Compose([
            transforms.Resize(IMAGE_SIZE),
            transforms.ToTensor()
        ])

    def __len__(self):

        return len(self.images)

    def __getitem__(
        self,
        idx
    ):

        image_name = self.images[idx]

        image_path = os.path.join(
            self.image_dir,
            image_name
        )

        mask_path = os.path.join(
            self.mask_dir,
            image_name
        )

        image = Image.open(
            image_path
        ).convert("RGB")

        mask = Image.open(
            mask_path
        ).convert("L")

        image = self.transform(
            image
        )

        mask = self.transform(
            mask
        )

        mask = (
            mask > 0.5
        ).float()

        return image, mask


# =====================================================
# DATALOADERS
# =====================================================

train_dataset = AnatomyDataset(
    TRAIN_IMAGES,
    TRAIN_MASKS
)

val_dataset = AnatomyDataset(
    VAL_IMAGES,
    VAL_MASKS
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False
)


# =====================================================
# MODEL
# =====================================================

model = AttentionUnet(
    spatial_dims=2,
    in_channels=3,
    out_channels=1,
    channels=(64, 128, 256, 512),
    strides=(2, 2, 2)
).to(DEVICE)


# =====================================================
# LOSS FUNCTIONS
# =====================================================

dice_loss = DiceLoss(
    sigmoid=True
)

bce_loss = nn.BCEWithLogitsLoss()


def combined_loss(
    prediction,
    target
):

    return (
        dice_loss(
            prediction,
            target
        )
        +
        bce_loss(
            prediction,
            target
        )
    )


# =====================================================
# OPTIMIZER
# =====================================================

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


# =====================================================
# TRAINING LOOP
# =====================================================

best_loss = float("inf")

best_model = copy.deepcopy(
    model.state_dict()
)


for epoch in range(EPOCHS):

    model.train()

    train_loss = 0

    progress = tqdm(
        train_loader,
        desc=f"Epoch {epoch+1}/{EPOCHS}"
    )

    for images, masks in progress:

        images = images.to(
            DEVICE
        )

        masks = masks.to(
            DEVICE
        )

        optimizer.zero_grad()

        outputs = model(
            images
        )

        loss = combined_loss(
            outputs,
            masks
        )

        loss.backward()

        optimizer.step()

        train_loss += loss.item()

        progress.set_postfix(
            loss=loss.item()
        )

    train_loss /= len(
        train_loader
    )

    # ----------------------------------------
    # VALIDATION
    # ----------------------------------------

    model.eval()

    val_loss = 0

    with torch.no_grad():

        for images, masks in val_loader:

            images = images.to(
                DEVICE
            )

            masks = masks.to(
                DEVICE
            )

            outputs = model(
                images
            )

            loss = combined_loss(
                outputs,
                masks
            )

            val_loss += loss.item()

    val_loss /= len(
        val_loader
    )

    print(
        f"Epoch {epoch+1}: "
        f"Train={train_loss:.4f} "
        f"Val={val_loss:.4f}"
    )

    # ----------------------------------------
    # SAVE BEST MODEL
    # ----------------------------------------

    if val_loss < best_loss:

        best_loss = val_loss

        best_model = copy.deepcopy(
            model.state_dict()
        )

        os.makedirs(
            "weights",
            exist_ok=True
        )

        torch.save(
            best_model,
            MODEL_OUTPUT
        )

        print(
            f"Best model saved "
            f"(val_loss={val_loss:.4f})"
        )


print(
    f"Training complete."
)

print(
    f"Best validation loss: "
    f"{best_loss:.4f}"
)