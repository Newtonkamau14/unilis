import pytesseract
from pytesseract import Output

from config import (
    TESSERACT_CONFIG
)

from image_preprocessor import (
    preprocess_image
)

from logger import logger


def extract_text(
    image_path: str
):

    image = preprocess_image(
        image_path
    )

    text = pytesseract.image_to_string(
        image,
        config=TESSERACT_CONFIG
    )

    logger.info(
        f"OCR completed: {image_path}"
    )

    return text.strip()


def extract_confidence(
    image_path: str
):

    image = preprocess_image(
        image_path
    )

    data = pytesseract.image_to_data(
        image,
        output_type=Output.DICT
    )

    confidences = []

    for value in data["conf"]:

        try:

            score = float(value)

            if score >= 0:

                confidences.append(
                    score
                )

        except Exception:
            pass

    if not confidences:
        return 0.0

    return round(
        sum(confidences)
        / len(confidences),
        2
    )