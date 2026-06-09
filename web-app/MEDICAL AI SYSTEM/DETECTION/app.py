import os
import logging

from fastapi import FastAPI, HTTPException

from shared.schemas import (
    DetectionRequest,
    DetectionResponse,
    DetectionData,
    ImageDetectionResult,
    Detection,
    BoundingBox
)

from yolo_model import detector

from unet_model import (
    segment_and_save,
    create_overlay
)


# =====================================================
# LOGGING
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =====================================================
# FASTAPI APP
# =====================================================

app = FastAPI(
    title="Detection Service",
    version="1.0.0",
    description="YOLOv11 + Attention U-Net Detection Service"
)


# =====================================================
# OUTPUT DIRECTORIES
# =====================================================

MASK_DIR = "output/masks"
OVERLAY_DIR = "output/overlays"
DETECTION_DIR = "output/detections"

os.makedirs(MASK_DIR, exist_ok=True)
os.makedirs(OVERLAY_DIR, exist_ok=True)
os.makedirs(DETECTION_DIR, exist_ok=True)


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "detection"
    }


# =====================================================
# DETECTION ENDPOINT
# =====================================================

@app.post(
    "/detect",
    response_model=DetectionResponse
)
def detect(request: DetectionRequest):

    try:

        results = []

        for image_path in request.image_paths:

            # ------------------------------------------
            # VALIDATE FILE EXISTS
            # ------------------------------------------

            if not os.path.exists(image_path):

                logger.warning(
                    f"Image not found: {image_path}"
                )

                continue

            filename = os.path.splitext(
                os.path.basename(image_path)
            )[0]

            logger.info(
                f"Processing image: {image_path}"
            )

            # ------------------------------------------
            # YOLO OBJECT DETECTION
            # ------------------------------------------

            yolo_results = detector.detect_objects(
                image_path
            )

            detections = []

            for item in yolo_results:

                detections.append(

                    Detection(
                        label=item["label"],

                        confidence=item["confidence"],

                        bbox=BoundingBox(
                            x1=item["bbox"]["x1"],
                            y1=item["bbox"]["y1"],
                            x2=item["bbox"]["x2"],
                            y2=item["bbox"]["y2"]
                        )
                    )
                )

            # ------------------------------------------
            # SAVE DETECTION IMAGE
            # ------------------------------------------

            detection_image = os.path.join(
                DETECTION_DIR,
                f"{filename}_detected.png"
            )

            detector.save_predictions(
                image_path,
                detection_image
            )

            # ------------------------------------------
            # ATTENTION U-NET SEGMENTATION
            # ------------------------------------------

            segmentation_mask = os.path.join(
                MASK_DIR,
                f"{filename}_mask.png"
            )

            segment_and_save(
                image_path,
                segmentation_mask
            )

            # ------------------------------------------
            # OVERLAY IMAGE
            # ------------------------------------------

            overlay_image = os.path.join(
                OVERLAY_DIR,
                f"{filename}_overlay.png"
            )

            create_overlay(
                image_path,
                overlay_image
            )

            # ------------------------------------------
            # STORE PAGE RESULT
            # ------------------------------------------

            results.append(

                ImageDetectionResult(

                    image_path=image_path,

                    detections=detections,

                    segmentation_mask=segmentation_mask,

                    detection_image=detection_image,

                    overlay_image=overlay_image
                )
            )

        # ------------------------------------------
        # NO VALID IMAGES
        # ------------------------------------------

        if len(results) == 0:

            raise HTTPException(
                status_code=404,
                detail="No valid images found."
            )

        logger.info(
            f"Detection completed. "
            f"Processed {len(results)} images."
        )

        return DetectionResponse(

            status="success",

            data=DetectionData(
                results=results
            ),

            error=None
        )

    except HTTPException as e:

        raise e

    except Exception as e:

        logger.exception(
            "Detection service failed"
        )

        return DetectionResponse(
            status="error",
            data=None,
            error=str(e)
        )


# =====================================================
# ROOT ENDPOINT
# =====================================================

@app.get("/")
def root():

    return {
        "service": "Detection Service",
        "model_1": "YOLOv11",
        "model_2": "Attention U-Net",
        "status": "running"
    }
    