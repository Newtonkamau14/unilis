from pydantic import BaseModel
from typing import List, Optional, Any


# -------------------------
# STANDARD RESPONSE WRAPPER
# -------------------------
class BaseResponse(BaseModel):
    status: str
    data: Optional[Any] = None
    error: Optional[str] = None


# -------------------------
# INGESTION CONTRACTS
# -------------------------
class IngestionRequest(BaseModel):
    file_path: str


class IngestionData(BaseModel):
    image_paths: List[str]


class IngestionResponse(BaseResponse):
    data: Optional[IngestionData]


# -------------------------
# DETECTION CONTRACTS
# -------------------------

class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class Detection(BaseModel):
    label: str
    bbox: BoundingBox
    confidence: float


class ImageDetectionResult(BaseModel):

    image_path: str

    detections: List[Detection]

    segmentation_mask: str

    detection_image: str

    overlay_image: str


class DetectionRequest(BaseModel):

    image_paths: List[str]


class DetectionData(BaseModel):

    results: List[ImageDetectionResult]


class DetectionResponse(BaseResponse):

    data: Optional[DetectionData]

# -------------------------
# OCR CONTRACTS
# -------------------------
class OCRText(BaseModel):
    text: str
    bbox: BoundingBox


class OCRRequest(BaseModel):
    image_path: str
    detections: List[Detection]
    segmentation_mask: str


class OCRData(BaseModel):
    recognized_text: List[OCRText]
    embeddings: List[float]


class OCRResponse(BaseResponse):
    data: Optional[OCRData]


# -------------------------
# SCORING CONTRACTS
# -------------------------
class ScoringRequest(BaseModel):
    detections: List[Detection]
    recognized_text: List[OCRText]
    embeddings: List[float]


class ScoringData(BaseModel):
    final_score: float
    label_accuracy: float
    structure_accuracy: float


class ScoringResponse(BaseResponse):
    data: Optional[ScoringData]


# -------------------------
# EXPLAINABILITY CONTRACTS
# -------------------------
class ExplainRequest(BaseModel):
    image_path: str
    detections: List[Detection]
    score: float


class ExplainData(BaseModel):
    heatmap_path: str
    feedback: str


class ExplainResponse(BaseResponse):
    data: Optional[ExplainData]