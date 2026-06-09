from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel import Session
from pydantic import BaseModel

from app.core.database import get_session
from app.core.deps import get_current_user
from app.modules.users.model import User
from .schema import OcrResponse
from .service import OcrService


class FileNamePayload(BaseModel):
    file_name: str

router = APIRouter(prefix="/ocr")


@router.post("/extract", response_model=OcrResponse)
async def extract_ocr(file: UploadFile = File(...)) -> dict:
    return await OcrService.extract_reading(file)

@router.post("/scan", response_model=OcrResponse)
async def scan_ocr(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        result = await OcrService.scan_meter_image(
            session,
            current_user,
            file
        )

        print("OCR SCAN RESULT:", result)

        return result

    except Exception as exc:
        import traceback

        print("\n===== OCR SCAN ERROR =====")
        traceback.print_exc()
        print("==========================\n")

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

@router.post("/extract-from-bucket", response_model=OcrResponse)
def extract_from_bucket(payload: FileNamePayload) -> dict:
    """Run OCR on a file that already exists in the configured Filebase bucket.

    Body: { "file_name": "meter_...jpg" }
    """
    return OcrService.extract_from_bucket(payload.file_name)
