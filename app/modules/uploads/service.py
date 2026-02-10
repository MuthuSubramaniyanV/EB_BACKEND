import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from .repository import FilebaseRepository

repo = FilebaseRepository()

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


class MeterService:
    @staticmethod
    async def process_meter_upload(file):
        content = await file.read()

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(400, "Unsupported file type")

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, "File too large")

        ext = "jpg" if file.content_type == "image/jpeg" else "png"
        file_name = f"meter_{uuid.uuid4()}.{ext}"

        image_url = repo.upload_file(
            content,
            file_name,
            file.content_type,
        )

        timestamp = datetime.now(timezone.utc)

        saved = repo.save_metadata_to_db(
            file_name=file_name,
            image_url=image_url,
            timestamp=timestamp,
            status="pending_ocr",
        )

        return {
            "id": saved.id,
            "image_url": saved.image_url,
            "timestamp": saved.timestamp,
            "status": saved.status,
        }
