from pathlib import Path

from shared.constants import (
    SUPPORTED_IMAGE_TYPES
)


def validate_image(
    image_path: str
) -> bool:

    extension = (
        Path(image_path)
        .suffix
        .lower()
    )

    return (
        extension
        in SUPPORTED_IMAGE_TYPES
    )