import uuid
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException
from sqlmodel import Session

from app.core.config import settings
from app.modules.uploads.model import MeterUpload
from app.modules.uploads.repository import UploadRepository, filebase

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


class MeterCaptureService:
    @staticmethod
    def capture_remote_image(session: Session, user_id: int) -> MeterUpload:
        camera_url = settings.ESP32_CAMERA_URL
        if not camera_url:
            raise HTTPException(
                status_code=500,
                detail="ESP32 camera URL is not configured",
            )

        request = Request(camera_url, headers={"User-Agent": "MeterX Backend"})
        try:
            with urlopen(request, timeout=15) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=502,
                        detail=f"ESP32 camera returned status {response.status}",
                    )

                content_type = response.getheader("Content-Type", "")
                media_type = content_type.split(";", 1)[0].strip().lower()
                if media_type not in ALLOWED_CONTENT_TYPES:
                    raise HTTPException(
                        status_code=502,
                        detail="ESP32 camera returned unsupported content type",
                    )

                content = response.read()
        except HTTPError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"ESP32 camera returned HTTP error {exc.code}",
            ) from exc
        except URLError as exc:
            raise HTTPException(
                status_code=502,
                detail="ESP32 camera is unreachable",
            ) from exc
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch image from ESP32 camera",
            ) from exc

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="Captured image is too large")

        ext = "jpg" if "jpeg" in media_type else "png"
        file_name = f"meter_{uuid.uuid4()}.{ext}"
        try:
            image_url = filebase.upload_image(content, file_name, content_type)
        except Exception as exc:
            raise HTTPException(
                status_code=502,
                detail="Failed to upload image to storage",
            ) from exc

        upload = MeterUpload(
            user_id=user_id,
            file_name=file_name,
            image_url=image_url,
            timestamp=datetime.now(timezone.utc),
            status="pending_ocr",
        )
        return UploadRepository.save(session, upload)
