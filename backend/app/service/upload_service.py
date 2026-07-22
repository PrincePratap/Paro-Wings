import logging
import os
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

logger = logging.getLogger(__name__)

UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR = UPLOAD_ROOT / "images"
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_safe_extension(filename: str) -> str:
    return Path(filename).suffix.lower()


async def upload_image(file: UploadFile, *, base_url: str) -> dict:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected.")

    extension = get_safe_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed.",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Image size must not exceed 10 MB.")

    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded.")

    ensure_upload_dir()
    file_name = f"{uuid4()}{extension}"
    file_path = UPLOAD_DIR / file_name

    try:
        with file_path.open("wb") as image_file:
            image_file.write(contents)
    except Exception as exc:
        logger.exception("Failed to write uploaded image")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save image.") from exc

    relative_path = f"/uploads/images/{file_name}"
    image_url = f"{base_url.rstrip('/')}{relative_path}"

    return {
        "image_url": image_url,
        "file_name": file_name,
    }
