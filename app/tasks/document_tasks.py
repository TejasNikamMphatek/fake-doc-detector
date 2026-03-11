from pathlib import Path

from app.worker.celery_worker import celery_app
from app.services.pdf_normalization_service import convert_pdf_to_images
from app.services.image_preprocessing_service import ImagePreprocessingService

preprocessor = ImagePreprocessingService()

PROCESSED_DIR = Path("storage/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


@celery_app.task
def process_document(file_path: str, detected_type: str):

    if detected_type == "application/pdf":
        image_paths = convert_pdf_to_images(file_path)
    else:
        image_paths = [file_path]

    processed_images = []

    for img_path in image_paths:

        img_name = Path(img_path).stem
        processed_output = PROCESSED_DIR / f"{img_name}_processed.png"

        processed_path = preprocessor.preprocess(
            image_path=img_path,
            output_path=str(processed_output)
        )

        processed_images.append(processed_path)

    return {
        "pages": len(processed_images),
        "processed_images": processed_images
    }