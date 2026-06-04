from typing import Dict
from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import Field


# =====================================================
# HEALTH
# =====================================================

class HealthResponse(BaseModel):

    service: str

    version: str

    status: str


# =====================================================
# EXPLAINABILITY REQUEST
# =====================================================

class ExplainabilityRequest(BaseModel):

    image_path: str = Field(
        ...,
        description="Input image path"
    )

    model_type: str = Field(
        ...,
        description=(
            "classification | "
            "detection | "
            "segmentation | "
            "assessment"
        )
    )

    model_name: str

    target_class: Optional[int] = None

    prediction_score: Optional[float] = None

    generate_gradcam: bool = True

    generate_gradcam_pp: bool = True

    generate_integrated_gradients: bool = True

    generate_shap: bool = True

    generate_lrp: bool = True

    generate_pdf_report: bool = True


# =====================================================
# ATTRIBUTION
# =====================================================

class AttributionScore(BaseModel):

    class_name: str

    contribution: float


# =====================================================
# EXPLANATION RESPONSE
# =====================================================

class ExplainabilityResponse(BaseModel):

    success: bool

    explanation_text: str

    confidence_score: float

    heatmap_path: Optional[str] = None

    overlay_path: Optional[str] = None

    attention_map_path: Optional[str] = None

    report_path: Optional[str] = None

    attribution_scores: Optional[
        Dict[str, float]
    ] = None


# =====================================================
# GRADCAM RESPONSE
# =====================================================

class GradCAMResponse(BaseModel):

    success: bool

    heatmap_path: str

    overlay_path: str


# =====================================================
# SHAP RESPONSE
# =====================================================

class SHAPResponse(BaseModel):

    success: bool

    explanation_path: str


# =====================================================
# REPORT RESPONSE
# =====================================================

class ReportResponse(BaseModel):

    success: bool

    report_path: str


# =====================================================
# ERROR RESPONSE
# =====================================================

class ErrorResponse(BaseModel):

    success: bool = False

    error: str