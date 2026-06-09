from datetime import datetime
from time import perf_counter
from typing import Dict

import numpy as np
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import File

from attribution_engine import AttributionEngine
from confidence_estimator import ConfidenceEstimator
from explanation_generator import ExplanationGenerator
from logger import logger
from report_generator import ReportGenerator

from schemas import (
    ExplainRequest,
    ExplainResponse,
    ExplainData,
    ResponseMetadata
)


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Medical AI Explainability Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# =====================================================
# SERVICES
# =====================================================

explanation_generator = (
    ExplanationGenerator()
)

report_generator = (
    ReportGenerator()
)

attribution_engine = (
    AttributionEngine()
)

confidence_estimator = (
    ConfidenceEstimator()
)


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
async def health():

    return {
        "status": "healthy",
        "service": "EXPLAINABILITY",
        "timestamp":
        datetime.utcnow().isoformat()
    }


# =====================================================
# ATTRIBUTION SUMMARY
# =====================================================

@app.post(
    "/attribution/summary"
)
async def attribution_summary(
    attribution_map: list
):

    try:

        attribution_map = np.array(
            attribution_map,
            dtype=np.float32
        )

        result = (
            attribution_engine
            .build_explanation_summary(
                attribution_map
            )
        )

        return {
            "status": "success",
            "data": result
        }

    except Exception as e:

        logger.exception(
            "Attribution summary failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# CONFIDENCE
# =====================================================

@app.post(
    "/confidence"
)
async def confidence(
    attribution_map: list
):

    try:

        attribution_map = np.array(
            attribution_map,
            dtype=np.float32
        )

        confidence_score = (
            confidence_estimator
            .explanation_confidence(
                attribution_map
            )
        )

        confidence_level = (
            confidence_estimator
            .confidence_level(
                confidence_score
            )
        )

        return {
            "status": "success",
            "confidence_score":
            confidence_score,

            "confidence_level":
            confidence_level
        }

    except Exception as e:

        logger.exception(
            "Confidence estimation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# EXPLAIN
# =====================================================

@app.post(
    "/explain",
    response_model=ExplainResponse
)
async def explain(
    request: ExplainRequest
):

    start_time = perf_counter()

    try:

        explanation_result = (
            explanation_generator
            .generate_full_explanation(
                submission_id=
                request.submission_id,

                score=request.score,

                grade="Pending",

                feedback=[],

                attribution_scores={},

                verification_data=None,

                scoring_breakdown=None,

                confidence_score=0.0
            )
        )

        explain_data = ExplainData(
            heatmap_path="",
            gradcam_path="",
            attention_map_path="",
            overlay_path="",

            attribution_scores=
            explanation_result[
                "attribution_scores"
            ],

            explanation=
            explanation_result[
                "student_explanation"
            ]
        )

        metadata = (
            ResponseMetadata(
                service=
                "EXPLAINABILITY",

                processing_time_ms=
                (
                    perf_counter()
                    -
                    start_time
                )
                * 1000
            )
        )

        return ExplainResponse(
            status="success",
            data=explain_data,
            metadata=metadata
        )

    except Exception as e:

        logger.exception(
            "Explain endpoint failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# REPORT GENERATION
# =====================================================

@app.post(
    "/report/student"
)
async def generate_student_report(
    request: Dict
):

    try:

        report_path = (
            report_generator
            .generate_student_report(
                submission_id=
                request[
                    "submission_id"
                ],

                score=
                request[
                    "score"
                ],

                grade=
                request[
                    "grade"
                ],

                feedback=
                request.get(
                    "feedback",
                    []
                ),

                explanation=
                request.get(
                    "explanation",
                    ""
                ),

                breakdown=
                request.get(
                    "breakdown",
                    {}
                ),

                heatmap_path=
                request.get(
                    "heatmap_path"
                ),

                attention_map_path=
                request.get(
                    "attention_map_path"
                ),

                overlay_path=
                request.get(
                    "overlay_path"
                )
            )
        )

        return {
            "status":
            "success",

            "report_path":
            report_path
        }

    except Exception as e:

        logger.exception(
            "Student report failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# INSTRUCTOR REPORT
# =====================================================

@app.post(
    "/report/instructor"
)
async def generate_instructor_report(
    request: Dict
):

    try:

        report_path = (
            report_generator
            .generate_instructor_report(
                submission_id=
                request[
                    "submission_id"
                ],

                score=
                request[
                    "score"
                ],

                grade=
                request[
                    "grade"
                ],

                confidence_score=
                request.get(
                    "confidence_score",
                    0.0
                ),

                explanation=
                request.get(
                    "explanation",
                    ""
                ),

                attribution_scores=
                request.get(
                    "attribution_scores",
                    {}
                ),

                verification_results=
                request.get(
                    "verification_results",
                    {}
                ),

                scoring_breakdown=
                request.get(
                    "scoring_breakdown",
                    {}
                ),

                heatmap_path=
                request.get(
                    "heatmap_path"
                ),

                attention_map_path=
                request.get(
                    "attention_map_path"
                ),

                overlay_path=
                request.get(
                    "overlay_path"
                )
            )
        )

        return {
            "status":
            "success",

            "report_path":
            report_path
        }

    except Exception as e:

        logger.exception(
            "Instructor report failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# COMBINED REPORTS
# =====================================================

@app.post(
    "/report/all"
)
async def generate_all_reports(
    request: Dict
):

    try:

        reports = (
            report_generator
            .generate_reports(
                submission_id=
                request[
                    "submission_id"
                ],

                score=
                request[
                    "score"
                ],

                grade=
                request[
                    "grade"
                ],

                feedback=
                request.get(
                    "feedback",
                    []
                ),

                explanation=
                request.get(
                    "explanation",
                    ""
                ),

                breakdown=
                request.get(
                    "breakdown",
                    {}
                ),

                confidence_score=
                request.get(
                    "confidence_score",
                    0.0
                ),

                attribution_scores=
                request.get(
                    "attribution_scores",
                    {}
                ),

                verification_results=
                request.get(
                    "verification_results",
                    {}
                ),

                heatmap_path=
                request.get(
                    "heatmap_path"
                ),

                attention_map_path=
                request.get(
                    "attention_map_path"
                ),

                overlay_path=
                request.get(
                    "overlay_path"
                )
            )
        )

        return {
            "status":
            "success",

            "reports":
            reports
        }

    except Exception as e:

        logger.exception(
            "Combined report generation failed"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# ROOT
# =====================================================

@app.get("/")
async def root():

    return {
        "service":
        "Medical AI Explainability",

        "version":
        "1.0.0",

        "status":
        "running"
    }