from fastapi import APIRouter, UploadFile, File
from .schema import OcrResponse
from .service import OcrService

router = APIRouter(prefix="/ocr")


@router.post("/extract", response_model=OcrResponse)
async def extract_ocr(file: UploadFile = File(...)) -> dict:
    return await OcrService.extract_reading(file)
