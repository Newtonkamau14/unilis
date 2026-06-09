from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import settings
from logger import logger


class ReportGenerator:

    def __init__(self):

        self.styles = (
            getSampleStyleSheet()
        )

        self.student_dir = Path(
            "reports/student_feedback"
        )

        self.instructor_dir = Path(
            "reports/instructor_feedback"
        )

        self.student_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.instructor_dir.mkdir(
            parents=True,
            exist_ok=True
        )

    # ==================================================
    # HELPERS
    # ==================================================

    def _safe_image(
        self,
        image_path: Optional[str],
        width=14 * cm
    ):

        try:

            if (
                image_path
                and Path(image_path).exists()
            ):

                return Image(
                    image_path,
                    width=width,
                    preserveAspectRatio=True
                )

        except Exception:

            logger.exception(
                "Failed loading image"
            )

        return None

    def _build_table(
        self,
        rows
    ):

        table = Table(rows)

        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey,
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.black,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                ]
            )
        )

        return table

    # ==================================================
    # STUDENT REPORT
    # ==================================================

    def generate_student_report(
        self,
        submission_id: str,
        score: float,
        grade: str,
        feedback: List[str],
        explanation: str,
        breakdown: Dict,
        heatmap_path: Optional[str] = None,
        attention_map_path: Optional[str] = None,
        overlay_path: Optional[str] = None,
    ):

        try:

            report_path = (
                self.student_dir
                /
                f"{submission_id}.pdf"
            )

            doc = SimpleDocTemplate(
                str(report_path)
            )

            content = []

            content.append(
                Paragraph(
                    "Medical Diagram Assessment Report",
                    self.styles["Title"]
                )
            )

            content.append(
                Spacer(1, 10)
            )

            content.append(
                Paragraph(
                    f"Submission ID: {submission_id}",
                    self.styles["Normal"]
                )
            )

            content.append(
                Paragraph(
                    f"Generated: {datetime.utcnow()}",
                    self.styles["Normal"]
                )
            )

            content.append(
                Spacer(1, 10)
            )

            score_table = self._build_table(
                [
                    [
                        "Final Score",
                        "Grade"
                    ],
                    [
                        str(score),
                        grade
                    ]
                ]
            )

            content.append(
                score_table
            )

            content.append(
                Spacer(1, 15)
            )

            content.append(
                Paragraph(
                    "Score Breakdown",
                    self.styles["Heading2"]
                )
            )

            breakdown_rows = [
                ["Metric", "Score"]
            ]

            for k, v in breakdown.items():

                breakdown_rows.append(
                    [
                        str(k),
                        str(v)
                    ]
                )

            content.append(
                self._build_table(
                    breakdown_rows
                )
            )

            content.append(
                Spacer(1, 15)
            )

            content.append(
                Paragraph(
                    "Feedback",
                    self.styles["Heading2"]
                )
            )

            for item in feedback:

                content.append(
                    Paragraph(
                        f"• {item}",
                        self.styles["BodyText"]
                    )
                )

            content.append(
                Spacer(1, 15)
            )

            content.append(
                Paragraph(
                    "Explanation",
                    self.styles["Heading2"]
                )
            )

            content.append(
                Paragraph(
                    explanation,
                    self.styles["BodyText"]
                )
            )

            for image_path in [
                heatmap_path,
                attention_map_path,
                overlay_path
            ]:

                image = self._safe_image(
                    image_path
                )

                if image:

                    content.append(
                        Spacer(1, 10)
                    )

                    content.append(
                        image
                    )

            doc.build(content)

            logger.info(
                f"Student report generated: "
                f"{report_path}"
            )

            return str(report_path)

        except Exception as e:

            logger.exception(
                "Student report failed"
            )

            raise e

    # ==================================================
    # INSTRUCTOR REPORT
    # ==================================================

    def generate_instructor_report(
        self,
        submission_id: str,
        score: float,
        grade: str,
        confidence_score: float,
        explanation: str,
        attribution_scores: Dict,
        verification_results: Optional[
            Dict
        ] = None,
        scoring_breakdown: Optional[
            Dict
        ] = None,
        heatmap_path: Optional[str] = None,
        attention_map_path: Optional[str] = None,
        overlay_path: Optional[str] = None,
    ):

        try:

            report_path = (
                self.instructor_dir
                /
                f"{submission_id}.pdf"
            )

            doc = SimpleDocTemplate(
                str(report_path)
            )

            content = []

            content.append(
                Paragraph(
                    "Instructor Assessment Report",
                    self.styles["Title"]
                )
            )

            content.append(
                Spacer(1, 10)
            )

            content.append(
                Paragraph(
                    f"Submission ID: {submission_id}",
                    self.styles["Normal"]
                )
            )

            content.append(
                Paragraph(
                    f"Generated: {datetime.utcnow()}",
                    self.styles["Normal"]
                )
            )

            content.append(
                Spacer(1, 10)
            )

            summary_table = (
                self._build_table(
                    [
                        [
                            "Score",
                            "Grade",
                            "Confidence"
                        ],
                        [
                            str(score),
                            grade,
                            str(
                                round(
                                    confidence_score,
                                    4
                                )
                            )
                        ]
                    ]
                )
            )

            content.append(
                summary_table
            )

            content.append(
                Spacer(1, 15)
            )

            if scoring_breakdown:

                content.append(
                    Paragraph(
                        "Scoring Breakdown",
                        self.styles["Heading2"]
                    )
                )

                rows = [
                    [
                        "Metric",
                        "Score"
                    ]
                ]

                for k, v in (
                    scoring_breakdown.items()
                ):

                    rows.append(
                        [
                            str(k),
                            str(v)
                        ]
                    )

                content.append(
                    self._build_table(
                        rows
                    )
                )

            if attribution_scores:

                content.append(
                    Spacer(1, 15)
                )

                content.append(
                    Paragraph(
                        "Attribution Scores",
                        self.styles["Heading2"]
                    )
                )

                rows = [
                    [
                        "Feature",
                        "Importance"
                    ]
                ]

                for (
                    feature,
                    score_value
                ) in (
                    attribution_scores.items()
                ):

                    rows.append(
                        [
                            feature,
                            str(
                                round(
                                    score_value,
                                    4
                                )
                            )
                        ]
                    )

                content.append(
                    self._build_table(
                        rows
                    )
                )

            if verification_results:

                content.append(
                    Spacer(1, 15)
                )

                content.append(
                    Paragraph(
                        "Verification Summary",
                        self.styles["Heading2"]
                    )
                )

                for (
                    key,
                    value
                ) in (
                    verification_results.items()
                ):

                    content.append(
                        Paragraph(
                            f"{key}: {value}",
                            self.styles["BodyText"]
                        )
                    )

            content.append(
                Spacer(1, 15)
            )

            content.append(
                Paragraph(
                    "Explainability Summary",
                    self.styles["Heading2"]
                )
            )

            content.append(
                Paragraph(
                    explanation,
                    self.styles["BodyText"]
                )
            )

            for image_path in [
                heatmap_path,
                attention_map_path,
                overlay_path
            ]:

                image = self._safe_image(
                    image_path
                )

                if image:

                    content.append(
                        Spacer(1, 10)
                    )

                    content.append(
                        image
                    )

            content.append(
                PageBreak()
            )

            doc.build(content)

            logger.info(
                f"Instructor report generated: "
                f"{report_path}"
            )

            return str(report_path)

        except Exception as e:

            logger.exception(
                "Instructor report failed"
            )

            raise e

    # ==================================================
    # COMBINED REPORTS
    # ==================================================

    def generate_reports(
        self,
        submission_id: str,
        score: float,
        grade: str,
        feedback: List[str],
        explanation: str,
        breakdown: Dict,
        confidence_score: float,
        attribution_scores: Dict,
        verification_results: Optional[
            Dict
        ] = None,
        heatmap_path: Optional[str] = None,
        attention_map_path: Optional[str] = None,
        overlay_path: Optional[str] = None,
    ):

        student_report = (
            self.generate_student_report(
                submission_id=submission_id,
                score=score,
                grade=grade,
                feedback=feedback,
                explanation=explanation,
                breakdown=breakdown,
                heatmap_path=heatmap_path,
                attention_map_path=attention_map_path,
                overlay_path=overlay_path,
            )
        )

        instructor_report = (
            self.generate_instructor_report(
                submission_id=submission_id,
                score=score,
                grade=grade,
                confidence_score=confidence_score,
                explanation=explanation,
                attribution_scores=attribution_scores,
                verification_results=verification_results,
                scoring_breakdown=breakdown,
                heatmap_path=heatmap_path,
                attention_map_path=attention_map_path,
                overlay_path=overlay_path,
            )
        )

        return {
            "student_report":
            student_report,

            "instructor_report":
            instructor_report
        }