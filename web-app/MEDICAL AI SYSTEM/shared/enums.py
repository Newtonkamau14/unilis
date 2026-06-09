from enum import Enum


class ServiceName(str, Enum):
    GATEWAY = "gateway"
    INGESTION = "ingestion"
    DETECTION = "detection"
    OCR = "ocr"
    MULTIMODAL = "multimodal_verification"
    SCORING = "scoring"
    EXPLAINABILITY = "explainability"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class Grade(str, Enum):
    EXCELLENT = "Excellent"
    VERY_GOOD = "Very Good"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"


class DiagramType(str, Enum):
    ANATOMY = "anatomy"
    PHYSIOLOGY = "physiology"
    HISTOLOGY = "histology"