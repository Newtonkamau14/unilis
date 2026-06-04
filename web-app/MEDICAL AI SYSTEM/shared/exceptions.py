class MedicalAISystemException(Exception):
    """Base exception."""


class InvalidImageException(MedicalAISystemException):
    """Raised when image validation fails."""


class OCRException(MedicalAISystemException):
    """Raised during OCR failure."""


class DetectionException(MedicalAISystemException):
    """Raised during detection failure."""


class SegmentationException(MedicalAISystemException):
    """Raised during segmentation failure."""


class VerificationException(MedicalAISystemException):
    """Raised during multimodal verification."""


class ScoringException(MedicalAISystemException):
    """Raised during scoring."""


class ExplainabilityException(MedicalAISystemException):
    """Raised during explainability generation."""