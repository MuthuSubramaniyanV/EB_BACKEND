from fastapi import UploadFile
from app.utils.ocr import perform_ocr


class OcrService:
    @staticmethod
    async def extract_reading(file: UploadFile) -> dict:
        result = await perform_ocr(file)
        return result
