import uuid
import json
from pathlib import Path


def generate_submission_id() -> str:

    return str(uuid.uuid4())


def save_json(
    data: dict,
    output_path: str
) -> None:

    path = Path(output_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_json(
    file_path: str
) -> dict:

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)