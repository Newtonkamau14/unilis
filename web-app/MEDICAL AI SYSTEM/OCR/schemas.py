from pydantic import BaseModel
from typing import List


class OCRRequest(BaseModel):
    submission_id: str
    page_number: int
    image_path: str


class OCRBatchPage(BaseModel):
    page_number: int
    image_path: str


class OCRBatchRequest(BaseModel):
    submission_id: str
    pages: List[OCRBatchPage]


class OCRVerification(BaseModel):
    is_valid: bool
    character_count: int
    word_count: int


class OCRResponse(BaseModel):
    status: str
    submission_id: str
    page_number: int
    image_path: str
    ocr_confidence: float
    confidence_passed: bool
    verified: OCRVerification
    text: str