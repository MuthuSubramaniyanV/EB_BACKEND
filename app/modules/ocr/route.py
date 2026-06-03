from fastapi import APIRouter, UploadFile, File
from .schema import OcrResponse
from .service import OcrService
from pydantic import BaseModel


class FileNamePayload(BaseModel):
    file_name: str

router = APIRouter(prefix="/ocr")


@router.post("/extract", response_model=OcrResponse)
async def extract_ocr(file: UploadFile = File(...)) -> dict:
    return await OcrService.extract_reading(file)


@router.post("/extract-from-bucket", response_model=OcrResponse)
def extract_from_bucket(payload: FileNamePayload) -> dict:
    """Run OCR on a file that already exists in the configured Filebase bucket.

    Body: { "file_name": "meter_...jpg" }
    """
    return OcrService.extract_from_bucket(payload.file_name)
