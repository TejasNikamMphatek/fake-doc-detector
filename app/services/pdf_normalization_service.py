from pdf2image import convert_from_path
from pathlib import Path
import uuid


NORMALIZED_DIR = Path("storage/normalized")
NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)


def convert_pdf_to_images(pdf_path: Path, dpi: int = 600):
    pages = convert_from_path(
        pdf_path=str(pdf_path),
        dpi=dpi,
        fmt="png"
    )

    image_paths = []

    for idx, page in enumerate(pages):
        filename = f"{pdf_path.stem}_page_{idx+1}_{uuid.uuid4().hex[:6]}.png"
        output_path = NORMALIZED_DIR / filename

        page.save(output_path, "PNG")
        image_paths.append(str(output_path))

    return image_paths