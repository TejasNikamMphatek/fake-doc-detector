from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import hashlib
import uuid

from app.utils.file_signature_validator import validate_file_signature
from app.tasks.document_tasks import process_document
from celery.result import AsyncResult
from app.worker.celery_worker import celery_app
router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = 20


def calculate_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    contents = await file.read()

    is_valid, detected_type = validate_file_signature(contents)

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type"
        )

    size_mb = len(contents) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail="File too large"
        )

    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    file_hash = calculate_sha256(file_path)

    # Send task to Celery
    task = process_document.delay(str(file_path), detected_type)

    return {
        "filename": unique_filename,
        "sha256": file_hash,
        "task_id": task.id,
        "message": "File uploaded. Processing started in background."
    }






@router.get("/task/{task_id}")
def get_task_status(task_id: str):

    task_result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task_result.status
    }

    if task_result.status == "SUCCESS":
        response["result"] = task_result.result

    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)

    elif task_result.status == "PROCESSING":
        response["progress"] = task_result.info

    return response