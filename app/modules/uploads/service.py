import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlmodel import Session
from app.modules.uploads.model import MeterUpload
from app.modules.uploads.repository import UploadRepository, filebase

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


class UploadService:
    @staticmethod
    async def process_meter_upload(session: Session, file, user_id: int) -> MeterUpload:
        content = await file.read()

        if file.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        ext = "jpg" if file.content_type == "image/jpeg" else "png"
        file_name = f"meter_{uuid.uuid4()}.{ext}"
        image_url = filebase.upload_image(content, file_name, file.content_type)

        upload = MeterUpload(
            user_id=user_id,
            file_name=file_name,
            image_url=image_url,
            timestamp=datetime.now(timezone.utc),
            status="pending_ocr",
        )
        return UploadRepository.save(session, upload)

    @staticmethod
    def delete_upload(session: Session, upload: MeterUpload) -> None:
        filebase.delete_image(upload.file_name)
        UploadRepository.delete(session, upload)
