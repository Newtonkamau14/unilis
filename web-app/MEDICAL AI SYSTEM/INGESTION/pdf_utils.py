from pathlib import Path
import logging
import fitz


logger = logging.getLogger(__name__)


# =====================================================
# PDF VALIDATION
# =====================================================

def validate_pdf(
    file_bytes: bytes
) -> bool:

    try:

        with fitz.open(
            stream=file_bytes,
            filetype="pdf"
        ) as document:

            if len(document) == 0:

                raise ValueError(
                    "PDF contains no pages"
                )

        return True

    except Exception as e:

        logger.exception(
            f"Invalid PDF: {e}"
        )

        raise ValueError(
            "Uploaded file is not a valid PDF"
        )


# =====================================================
# PDF TO IMAGES
# =====================================================

def pdf_to_images(
    pdf_path: str,
    output_folder: str,
    dpi: int = 300
) -> list[str]:

    pdf_path = Path(pdf_path)

    output_folder = Path(
        output_folder
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF not found: "
            f"{pdf_path}"
        )

    image_paths = []

    zoom = dpi / 72

    try:

        with fitz.open(
            pdf_path
        ) as document:

            for page_number in range(
                len(document)
            ):

                page = document.load_page(
                    page_number
                )

                pix = page.get_pixmap(
                    matrix=fitz.Matrix(
                        zoom,
                        zoom
                    )
                )

                image_path = (
                    output_folder
                    / (
                        f"page_"
                        f"{page_number + 1}.png"
                    )
                )

                pix.save(
                    str(image_path)
                )

                image_paths.append(
                    str(image_path)
                )

        logger.info(
            f"Converted "
            f"{len(image_paths)} pages "
            f"from "
            f"{pdf_path.name}"
        )

        return image_paths

    except Exception as e:

        logger.exception(
            f"PDF conversion failed: "
            f"{e}"
        )

        raise