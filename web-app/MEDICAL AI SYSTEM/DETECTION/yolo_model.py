import os
import logging
import torch

from ultralytics import YOLO


# =====================================================
# CONFIGURATION
# =====================================================

MODEL_PATH = "weights/yolo11m_medical.pt"

CONFIDENCE_THRESHOLD = 0.30

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
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
# DETECTOR CLASS
# =====================================================

class MedicalDiagramDetector:

    def __init__(
        self,
        model_path=MODEL_PATH,
        confidence=CONFIDENCE_THRESHOLD
    ):

        self.model_path = model_path
        self.confidence = confidence

        self.model = self._load_model()

    # -------------------------------------------------

    def _load_model(self):

        if not os.path.exists(self.model_path):

            raise FileNotFoundError(
                f"YOLO model not found: {self.model_path}"
            )

        logger.info(
            f"Loading YOLO model: {self.model_path}"
        )

        model = YOLO(self.model_path)

        logger.info(
            f"YOLO loaded successfully on {DEVICE}"
        )

        return model

    # -------------------------------------------------

    def detect_objects(
        self,
        image_path
    ):

        if not os.path.exists(image_path):

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        try:

            results = self.model.predict(
                source=image_path,
                conf=self.confidence,
                device=DEVICE,
                verbose=False
            )

            detections = []

            for result in results:

                for box in result.boxes:

                    class_id = int(
                        box.cls.item()
                    )

                    detections.append({

                        "label":
                        self.model.names[class_id],

                        "confidence":
                        round(
                            float(box.conf.item()),
                            4
                        ),

                        "bbox": {

                            "x1":
                            int(box.xyxy[0][0]),

                            "y1":
                            int(box.xyxy[0][1]),

                            "x2":
                            int(box.xyxy[0][2]),

                            "y2":
                            int(box.xyxy[0][3])
                        }
                    })

            return detections

        except Exception as e:

            logger.error(
                f"Detection failed: {str(e)}"
            )

            raise

    # -------------------------------------------------

    def count_objects(
        self,
        detections
    ):

        counts = {}

        for detection in detections:

            label = detection["label"]

            counts[label] = (
                counts.get(label, 0) + 1
            )

        return counts

    # -------------------------------------------------

    def get_detection_summary(
        self,
        detections
    ):

        summary = {

            "total_objects":
            len(detections),

            "object_counts":
            self.count_objects(
                detections
            )
        }

        return summary

    # -------------------------------------------------

    def save_predictions(
        self,
        image_path,
        output_path
    ):

        if not os.path.exists(image_path):

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        results = self.model.predict(
            source=image_path,
            conf=self.confidence,
            device=DEVICE,
            verbose=False
        )

        annotated_image = results[0].plot()

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        import cv2

        cv2.imwrite(
            output_path,
            annotated_image
        )

        return output_path

    # -------------------------------------------------

    def detect_and_annotate(
        self,
        image_path,
        output_path
    ):

        detections = self.detect_objects(
            image_path
        )

        annotated = self.save_predictions(
            image_path,
            output_path
        )

        summary = self.get_detection_summary(
            detections
        )

        return {

            "detections":
            detections,

            "summary":
            summary,

            "annotated_image":
            annotated
        }


