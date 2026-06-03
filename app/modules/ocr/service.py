from fastapi import UploadFile
from app.utils.ocr import perform_ocr


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
