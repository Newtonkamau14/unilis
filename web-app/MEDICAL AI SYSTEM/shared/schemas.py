
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# RESPONSE METADATA
# =====================================================

class ResponseMetadata(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    service: Optional[str] = None

    processing_time_ms: Optional[float] = None


# =====================================================
# STANDARD RESPONSE WRAPPER
# =====================================================

class BaseResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True
    )

    status: str

    data: Optional[Any] = None

    error: Optional[str] = None

    metadata: Optional[ResponseMetadata] = None


# =====================================================
# SHARED REQUEST MODELS
# =====================================================

class SubmissionRequest(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

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

    segmentation_confidence: Optional[
        float
    ] = None


class ImageDetectionResult(BaseModel):
    image_path: str

    detections: List["Detection"]

    segmentation_mask: str

    detection_image: str

    overlay_image: str


class DetectionRequest(
    SubmissionRequest
):
    image_paths: List[str]


class DetectionData(BaseModel):
    results: List[
        ImageDetectionResult
    ]


class DetectionResponse(BaseResponse):
    data: Optional[
        "DetectionData"
    ] = None


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
    data: Optional[
        "OCRData"
    ] = None


# =====================================================
# MULTIMODAL VERIFICATION CONTRACTS
# =====================================================

class LabelMatch(BaseModel):
    component_name: str

    detected_label: str

    similarity_score: float

    matched: bool


class SpatialValidation(BaseModel):
    label: str

    distance_to_structure: float

    spatially_correct: bool


class VerificationRequest(
    SubmissionRequest
):
    detections: List[Detection]

    recognized_text: List[OCRText]

    embeddings: List[float]


class VerificationData(BaseModel):
    label_matches: List[
        LabelMatch
    ]

    spatial_validations: List[
        SpatialValidation
    ]

    semantic_similarity: float

    label_accuracy: float

    missing_labels: List[str]

    mismatched_labels: List[str]

    ontology_matches: List[str]


class VerificationResponse(
    BaseResponse
):
    data: Optional[
        "VerificationData"
    ] = None


# =====================================================
# SCORING CONTRACTS
# =====================================================

class ScoreBreakdown(BaseModel):
    completeness: float

    structural_accuracy: float

    label_correctness: float

    spatial_correctness: float

    diagram_quality: float


class ScoringRequest(
    SubmissionRequest
):
    detections: List[Detection]

    recognized_text: List[OCRText]

    embeddings: List[float]

    verification_data: VerificationData


class ScoringData(BaseModel):
    final_score: float

    grade: str

    breakdown: ScoreBreakdown

    feedback: List[str]


class ScoringResponse(
    BaseResponse
):
    data: Optional[
        "ScoringData"
    ] = None


# =====================================================
# EXPLAINABILITY CONTRACTS
# =====================================================

class ExplainRequest(ImageRequest):

    detections: List[Detection]

    score: float

    grade: Optional[str] = None

    feedback: Optional[List[str]] = None

    verification_data: Optional[
        VerificationData
    ] = None

    scoring_breakdown: Optional[
        ScoreBreakdown
    ] = None

    segmentation_mask: Optional[
        str
    ] = None

class ExplainData(BaseModel):

    heatmap_path: str

    gradcam_path: str

    attention_map_path: str

    overlay_path: str

    report_path: Optional[str]

    confidence_score: float

    attribution_scores: Dict[
        str,
        float
    ]

    explanation: str

    generated_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class ExplainResponse(
    BaseResponse
):
    data: Optional[
        "ExplainData"
    ] = None


# =====================================================
# FINAL ASSESSMENT REPORT
# =====================================================

class AssessmentReport(BaseModel):
    submission_id: str

    final_score: float

    grade: str

    detection_results: DetectionData

    ocr_results: OCRData

    verification_results: VerificationData

    scoring_results: ScoringData

    explainability_results: ExplainData

    generated_at: datetime = Field(
        default_factory=datetime.utcnow
    )


# =====================================================
# PIPELINE AGGREGATION CONTRACTS
# =====================================================

class PipelineResult(BaseModel):
    submission_id: str

    ingestion: Optional[
        IngestionData
    ] = None

    detection: Optional[
        DetectionData
    ] = None

    ocr: Optional[
        OCRData
    ] = None

    verification: Optional[
        VerificationData
    ] = None

    scoring: Optional[
        ScoringData
    ] = None

    explainability: Optional[
        ExplainData
    ] = None

    assessment_report: Optional[
        AssessmentReport
    ] = None

    completed_at: datetime = Field(
        default_factory=datetime.utcnow
    )


class PipelineResponse(
    BaseResponse
):
    data: Optional[
        PipelineResult
    ] = None


# =====================================================
# FORWARD REFERENCE RESOLUTION
# =====================================================

ImageDetectionResult.model_rebuild()

IngestionResponse.model_rebuild()

DetectionResponse.model_rebuild()

OCRResponse.model_rebuild()

VerificationResponse.model_rebuild()

ScoringResponse.model_rebuild()

ExplainResponse.model_rebuild()

PipelineResponse.model_rebuild()

