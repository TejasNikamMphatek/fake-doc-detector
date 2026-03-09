from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import hashlib
import uuid

from app.services.pdf_normalization_service import convert_pdf_to_images
from app.utils.file_signature_validator import validate_file_signature

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

    # Read file
    contents = await file.read()

    # Validate magic byte signature
    is_valid, detected_type = validate_file_signature(contents)

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file signature detected: {detected_type}"
        )

    # Validate file size
    size_mb = len(contents) / (1024 * 1024)

    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail="File too large (max 20MB)"
        )

    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}_{file.filename}"

    # Save file
    file_path = UPLOAD_DIR / unique_filename

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    # Generate SHA256
    file_hash = calculate_sha256(file_path)

    # Convert PDF → images
    if detected_type == "application/pdf":
        image_paths = convert_pdf_to_images(file_path)
    else:
        image_paths = [str(file_path)]

    return {
        "filename": unique_filename,
        "size_mb": round(size_mb, 2),
        "sha256": file_hash,
        "pages": len(image_paths),
        "normalized_images": image_paths,
        "message": "File uploaded and normalized successfully"
    }