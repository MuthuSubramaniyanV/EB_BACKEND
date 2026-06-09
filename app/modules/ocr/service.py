import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import UploadFile
from sqlmodel import Session

from app.services.filebase_service import FilebaseService
from app.utils.ocr import perform_ocr, perform_ocr_bytes
from app.modules.uploads.repository import UploadRepository
from app.modules.uploads.model import MeterUpload
from app.modules.readings.service import ReadingService


class OcrService:
    @staticmethod
    async def extract_reading(file: UploadFile) -> dict:
        result = await perform_ocr(file)
        return result

    @staticmethod
    def extract_from_bucket(file_name: str) -> dict:
        """Fetch image bytes from Filebase and perform OCR."""
        from app.utils.ocr import perform_ocr_from_bucket

        return perform_ocr_from_bucket(file_name)

    @staticmethod
    async def scan_meter_image(session: Session, current_user, file: UploadFile) -> dict:
        content = await file.read()
        if file.content_type not in {"image/jpeg", "image/png", "image/jpg"}:
            raise ValueError("Unsupported file type for OCR scan")

        ext = "jpg" if file.content_type == "image/jpeg" else "png"
        file_name = f"meter_{uuid.uuid4()}.{ext}"
        filebase = FilebaseService()
        image_url = filebase.upload_image(content, file_name, file.content_type)

        upload = MeterUpload(
            user_id=current_user.id,
            file_name=file_name,
            image_url=image_url,
            timestamp=datetime.now(timezone.utc),
            status="ocr_done",
        )
        UploadRepository.save(session, upload)

        ocr_result = perform_ocr_bytes(content, getattr(file, "filename", file_name))
        print("OCR_RESULT IS",ocr_result)
        reading = ReadingService.create_reading(
            session,
            current_user,
            {
                "reading_value": ocr_result["reading"],
                "ocr_confidence": ocr_result["confidence"],
                "upload_id": upload.id,
            },
        )

        return {
            "reading": reading.reading_value,
            "confidence": reading.ocr_confidence,
            "upload_id": upload.id,
            "image_url": upload.image_url,
        }
