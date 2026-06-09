import os
import copy
import random

from PIL import Image
from tqdm import tqdm

import torch
import torch.nn as nn

from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter

from torchvision import transforms
from torchvision.transforms import functional as TF

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

LOG_DIR = "runs/attention_unet"

IMAGE_SIZE = (512, 512)

BATCH_SIZE = 4

EPOCHS = 50

LEARNING_RATE = 1e-4

PATIENCE = 10

LR_PATIENCE = 3

MIN_LR = 1e-6


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
        mask_dir,
        augment=False
    ):

        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.augment = augment

        self.images = sorted(
            os.listdir(image_dir)
        )

        self.resize = transforms.Resize(
            IMAGE_SIZE
        )

        self.to_tensor = transforms.ToTensor()

    def __len__(self):

        return len(self.images)

    def augment_data(
        self,
        image,
        mask
    ):

        # Horizontal Flip
        if random.random() > 0.5:

            image = TF.hflip(image)
            mask = TF.hflip(mask)

        # Vertical Flip
        if random.random() > 0.5:

            image = TF.vflip(image)
            mask = TF.vflip(mask)

        # Rotation
        angle = random.uniform(
            -20,
            20
        )

        image = TF.rotate(
            image,
            angle
        )

        mask = TF.rotate(
            mask,
            angle
        )

        # Brightness
        brightness_factor = random.uniform(
            0.8,
            1.2
        )

        image = TF.adjust_brightness(
            image,
            brightness_factor
        )

        # Scaling

        scale = random.uniform(
            0.9,
            1.1
        )

        width, height = image.size

        new_height = int(height * scale)
        new_width = int(width * scale)

        image = TF.resize(
            image,
            (new_height, new_width)
        )

        mask = TF.resize(
            mask,
            (new_height, new_width)
        )

        image = TF.center_crop(
            image,
            IMAGE_SIZE
        )

        mask = TF.center_crop(
            mask,
            IMAGE_SIZE
        )

        return image, mask

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

        image = self.resize(
            image
        )

        mask = self.resize(
            mask
        )

        if self.augment:

            image, mask = self.augment_data(
                image,
                mask
            )

        image = self.to_tensor(
            image
        )

        mask = self.to_tensor(
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
    TRAIN_MASKS,
    augment=True
)

val_dataset = AnatomyDataset(
    VAL_IMAGES,
    VAL_MASKS,
    augment=False
)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=4,
    pin_memory=True
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=4,
    pin_memory=True
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
# METRICS
# =====================================================

def dice_score(
    prediction,
    target,
    smooth=1e-6
):

    prediction = torch.sigmoid(
        prediction
    )

    prediction = (
        prediction > 0.5
    ).float()

    intersection = (
        prediction * target
    ).sum()

    return (
        2 * intersection + smooth
    ) / (
        prediction.sum()
        +
        target.sum()
        +
        smooth
    )


def iou_score(
    prediction,
    target,
    smooth=1e-6
):

    prediction = torch.sigmoid(
        prediction
    )

    prediction = (
        prediction > 0.5
    ).float()

    intersection = (
        prediction * target
    ).sum()

    union = (
        prediction +
        target
    ).sum() - intersection

    return (
        intersection + smooth
    ) / (
        union + smooth
    )


# =====================================================
# OPTIMIZER
# =====================================================

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE
)


scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode="min",
    factor=0.5,
    patience=LR_PATIENCE,
    min_lr=MIN_LR
)


# =====================================================
# TENSORBOARD
# =====================================================

writer = SummaryWriter(
    LOG_DIR
)


# =====================================================
# TRAINING
# =====================================================

best_loss = float("inf")

early_stop_counter = 0

best_model = copy.deepcopy(
    model.state_dict()
)


for epoch in range(EPOCHS):

    # =============================================
    # TRAIN
    # =============================================

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

    # =============================================
    # VALIDATION
    # =============================================

    model.eval()

    val_loss = 0

    val_dice = 0

    val_iou = 0

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

            val_dice += dice_score(
                outputs,
                masks
            ).item()

            val_iou += iou_score(
                outputs,
                masks
            ).item()

    val_loss /= len(
        val_loader
    )

    val_dice /= len(
        val_loader
    )

    val_iou /= len(
        val_loader
    )

    # =============================================
    # SCHEDULER
    # =============================================

    scheduler.step(
        val_loss
    )

    # =============================================
    # TENSORBOARD LOGGING
    # =============================================

    writer.add_scalar(
        "Loss/Train",
        train_loss,
        epoch
    )

    writer.add_scalar(
        "Loss/Validation",
        val_loss,
        epoch
    )

    writer.add_scalar(
        "Metrics/Dice",
        val_dice,
        epoch
    )

    writer.add_scalar(
        "Metrics/IoU",
        val_iou,
        epoch
    )

    writer.add_scalar(
        "LearningRate",
        optimizer.param_groups[0]["lr"],
        epoch
    )

    # =============================================
    # PRINT METRICS
    # =============================================

    print(
        f"Epoch {epoch+1} | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {val_loss:.4f} | "
        f"Dice: {val_dice:.4f} | "
        f"IoU: {val_iou:.4f}"
    )

    # =============================================
    # SAVE BEST MODEL
    # =============================================

    if val_loss < best_loss:

        best_loss = val_loss

        early_stop_counter = 0

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
            f"(Val Loss={val_loss:.4f})"
        )

    else:

        early_stop_counter += 1

        print(
            f"Early Stopping Counter: "
            f"{early_stop_counter}/{PATIENCE}"
        )

    # =============================================
    # EARLY STOPPING
    # =============================================

    if early_stop_counter >= PATIENCE:

        print(
            "Early stopping triggered."
        )

        break


# =====================================================
# FINISH
# =====================================================

writer.close()

print(
    "\nTraining Complete"
)

print(
    f"Best Validation Loss: "
    f"{best_loss:.4f}"
)

print(
    f"Model Saved To: "
    f"{MODEL_OUTPUT}"
)