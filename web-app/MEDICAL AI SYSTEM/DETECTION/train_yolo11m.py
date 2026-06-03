import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime

import torch
from ultralytics import YOLO


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_YAML = "dataset_yolo/data.yaml"

PRETRAINED_MODEL = "yolo11m.pt"

PROJECT_NAME = "medical_ai_training"

RUN_NAME = "yolo11m_medical"

EPOCHS = 100

IMAGE_SIZE = 640

BATCH_SIZE = 8

PATIENCE = 20

WORKERS = 4

CACHE = False

AMP = True

DEVICE = 0 if torch.cuda.is_available() else "cpu"

OUTPUT_DIR = "runs"

FINAL_WEIGHTS_DIR = "weights"

FINAL_MODEL_NAME = "yolo11m_medical.pt"


# ============================================================
# LOGGING
# ============================================================

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename="logs/yolo_training.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def validate_dataset():
    """
    Ensure dataset exists before training.
    """

    if not os.path.exists(DATASET_YAML):
        raise FileNotFoundError(
            f"Dataset YAML not found: {DATASET_YAML}"
        )

    logger.info("Dataset validation successful.")


def save_training_config():
    """
    Save training parameters.
    """

    config = {
        "dataset": DATASET_YAML,
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "image_size": IMAGE_SIZE,
        "patience": PATIENCE,
        "device": str(DEVICE),
        "timestamp": str(datetime.now())
    }

    os.makedirs("training_configs", exist_ok=True)

    with open(
        "training_configs/yolo11m_config.json",
        "w"
    ) as f:
        json.dump(config, f, indent=4)

    logger.info("Training configuration saved.")


def save_best_model(best_model_path):
    """
    Copy best.pt into weights folder.
    """

    os.makedirs(FINAL_WEIGHTS_DIR, exist_ok=True)

    destination = os.path.join(
        FINAL_WEIGHTS_DIR,
        FINAL_MODEL_NAME
    )

    shutil.copy(
        best_model_path,
        destination
    )

    logger.info(
        f"Best model copied to {destination}"
    )

    print(f"\nSaved final model:\n{destination}")


def export_metrics(results):
    """
    Export training metrics.
    """

    metrics = {}

    try:

        metrics["fitness"] = float(results.fitness)

        if hasattr(results, "results_dict"):
            metrics.update(results.results_dict)

    except Exception:
        pass

    os.makedirs("training_metrics", exist_ok=True)

    with open(
        "training_metrics/yolo11m_metrics.json",
        "w"
    ) as f:
        json.dump(metrics, f, indent=4)

    logger.info("Metrics exported.")


# ============================================================
# TRAINING
# ============================================================

def train():

    logger.info(
        "Starting YOLO11m medical training..."
    )

    validate_dataset()

    save_training_config()

    print("\n===================================")
    print(" YOLO11M MEDICAL TRAINING")
    print("===================================\n")

    print(f"Device: {DEVICE}")
    print(f"Epochs: {EPOCHS}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Image Size: {IMAGE_SIZE}")

    model = YOLO(PRETRAINED_MODEL)

    results = model.train(

        # Dataset
        data=DATASET_YAML,

        # Training
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        workers=WORKERS,

        # Early stopping
        patience=PATIENCE,

        # Mixed precision
        amp=AMP,

        # Cache
        cache=CACHE,

        # Device
        device=DEVICE,

        # Saving
        project=OUTPUT_DIR,
        name=RUN_NAME,
        exist_ok=True,

        # Validation
        val=True,

        # ==================================
        # AUGMENTATION
        # ==================================

        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,

        degrees=10.0,

        translate=0.1,

        scale=0.5,

        shear=2.0,

        perspective=0.0001,

        flipud=0.0,

        fliplr=0.5,

        mosaic=1.0,

        mixup=0.2,

        copy_paste=0.1,

        erasing=0.2,

        # ==================================
        # OPTIMIZATION
        # ==================================

        optimizer="AdamW",

        lr0=0.001,

        lrf=0.01,

        weight_decay=0.0005,

        warmup_epochs=3,

        warmup_momentum=0.8,

        warmup_bias_lr=0.1,

        # ==================================
        # LOGGING
        # ==================================

        plots=True,

        save=True,

        save_period=5,

        verbose=True
    )

    logger.info("Training completed.")

    export_metrics(results)

    run_directory = os.path.join(
        OUTPUT_DIR,
        RUN_NAME,
        "weights"
    )

    best_model = os.path.join(
        run_directory,
        "best.pt"
    )

    if os.path.exists(best_model):

        save_best_model(best_model)

    else:

        logger.warning(
            "best.pt not found."
        )

        print(
            "\nWARNING: best.pt not found."
        )

    print("\nTraining Complete.\n")


# ============================================================
# RESUME TRAINING
# ============================================================

def resume_training(checkpoint_path):

    logger.info(
        f"Resuming from {checkpoint_path}"
    )

    model = YOLO(checkpoint_path)

    model.train(
        resume=True
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    try:

        train()

    except KeyboardInterrupt:

        logger.warning(
            "Training interrupted by user."
        )

        print(
            "\nTraining interrupted."
        )

    except Exception as e:

        logger.exception(str(e))

        print(
            f"\nTraining failed:\n{e}"
        )