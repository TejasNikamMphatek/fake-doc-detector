from pathlib import Path

from app.worker.celery_worker import celery_app
from app.services.pdf_normalization_service import convert_pdf_to_images
from app.services.image_preprocessing_service import ImagePreprocessingService

preprocessor = ImagePreprocessingService()

PROCESSED_DIR = Path("storage/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

@celery_app.task(bind=True, name="app.tasks.document_tasks.process_document")
def process_document(self, file_path: str, detected_type: str):

    file_path = Path(file_path)

    if detected_type == "application/pdf":
        image_paths = convert_pdf_to_images(file_path)
    else:
        image_paths = [file_path]

    total_pages = len(image_paths)
    processed_images = []

    for idx, img_path in enumerate(image_paths):

        img_path = Path(img_path)
        img_name = img_path.stem

        processed_output = PROCESSED_DIR / f"{img_name}_processed.png"

        processed_path = preprocessor.preprocess(
            image_path=str(img_path),
            output_path=str(processed_output)
        )

        processed_images.append(str(processed_path))

        # update progress
        self.update_state(
            state="PROCESSING",
            meta={
                "current": idx + 1,
                "total": total_pages
            }
        )

    return {
        "pages": total_pages,
        "processed_images": processed_images
    }