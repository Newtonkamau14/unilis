import json
from pathlib import Path

from config import OCR_OUTPUT_DIR


def save_ocr_result(
    submission_id: str,
    page_number: int,
    data: dict
):

    submission_dir = (
        OCR_OUTPUT_DIR /
        submission_id /
        "ocr"
    )

    submission_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        submission_dir /
        f"page_{page_number}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

    return str(
        output_file
    )