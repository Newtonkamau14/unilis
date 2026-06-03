from pdf2image import convert_from_path
import os


def pdf_to_images(pdf_path, output_folder):
    pages = convert_from_path(pdf_path)

    image_paths = []

    for i, page in enumerate(pages):
        image_path = os.path.join(
            output_folder,
            f"page_{i}.png"
        )

        page.save(image_path)

        image_paths.append(image_path)

    return image_paths
