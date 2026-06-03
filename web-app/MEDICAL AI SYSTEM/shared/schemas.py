from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


# =====================================================
# RESPONSE METADATA
# =====================================================

class ResponseMetadata(BaseModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    service: Optional[str] = None

    processing_time_ms: Optional[float] = None


# =====================================================
# STANDARD RESPONSE WRAPPER
# =====================================================

class BaseResponse(BaseModel):
    status: str

    data: Optional[Any] = None

    error: Optional[str] = None

    metadata: Optional[ResponseMetadata] = None


# =====================================================
# SHARED REQUEST MODELS
# =====================================================

class SubmissionRequest(BaseModel):
    submission_id: str

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class ImageRequest(SubmissionRequest):
    image_path: str


# =====================================================
# INGESTION CONTRACTS
# =====================================================

class IngestionRequest(BaseModel):
    file_path: str


class IngestionData(BaseModel):
    submission_id: str

    original_filename: str

    pdf_path: str

    image_paths: List[str]

    page_count: int

    uploaded_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class IngestionResponse(BaseResponse):
    data: Optional["IngestionData"] = None


# =====================================================
# DETECTION CONTRACTS
# =====================================================

class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int


class Detection(BaseModel):
    label: str

    bbox: BoundingBox

    confidence: float

    segmentation_confidence: Optional[float] = None


class ImageDetectionResult(BaseModel):
    image_path: str

    detections: List["Detection"]

    segmentation_mask: str

    detection_image: str

    overlay_image: str


class DetectionRequest(SubmissionRequest):
    image_paths: List[str]


class DetectionData(BaseModel):
    results: List[ImageDetectionResult]


class DetectionResponse(BaseResponse):
    data: Optional["DetectionData"] = None


# =====================================================
# OCR CONTRACTS
# =====================================================

class OCRText(BaseModel):
    text: str

    bbox: BoundingBox

    confidence: float


class OCRRequest(ImageRequest):
    detections: List[Detection]

    segmentation_mask: str


class OCRData(BaseModel):
    recognized_text: List[OCRText]

    embeddings: List[float]


class OCRResponse(BaseResponse):
    data: Optional["OCRData"] = None


# =====================================================
# SCORING CONTRACTS
# =====================================================

class ScoringRequest(SubmissionRequest):
    detections: List[Detection]

    recognized_text: List[OCRText]

    embeddings: List[float]


class ScoringData(BaseModel):
    final_score: float

    label_accuracy: float

    structure_accuracy: float

    feedback: Optional[str] = None


class ScoringResponse(BaseResponse):
    data: Optional["ScoringData"] = None


# =====================================================
# EXPLAINABILITY CONTRACTS
# =====================================================

class ExplainRequest(ImageRequest):
    detections: List[Detection]

    score: float


class ExplainData(BaseModel):
    heatmap_path: str

    feedback: str


class ExplainResponse(BaseResponse):
    data: Optional["ExplainData"] = None


# =====================================================
# PIPELINE AGGREGATION CONTRACTS
# =====================================================

class PipelineResult(BaseModel):
    submission_id: str

    ingestion: Optional[IngestionData] = None

    detection: Optional[DetectionData] = None

    ocr: Optional[OCRData] = None

    scoring: Optional[ScoringData] = None

    explainability: Optional[ExplainData] = None

    completed_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class PipelineResponse(BaseResponse):
    data: Optional[PipelineResult] = None


# =====================================================
# FORWARD REFERENCE RESOLUTION
# =====================================================

ImageDetectionResult.model_rebuild()

IngestionResponse.model_rebuild()

DetectionResponse.model_rebuild()

OCRResponse.model_rebuild()

ScoringResponse.model_rebuild()

ExplainResponse.model_rebuild()

PipelineResponse.model_rebuild()