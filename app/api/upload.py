from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import hashlib
import os
from app.services.pdf_normalization_service import convert_pdf_to_images
from pathlib import Path
router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_MB = 20
ALLOWED_TYPES = ["application/pdf"]


def calculate_sha256(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

# Convert PDF to images

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Validate content type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Validate file size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # Hash file
    file_hash = calculate_sha256(file_path)
    image_paths = convert_pdf_to_images(Path(file_path))
    return {
        "filename": file.filename,
        "size_mb": round(size_mb, 2),
        "sha256": file_hash,
        "pages": len(image_paths),
        "normalized_images": image_paths,
        "message": "File uploaded and normalized successfully"
    }