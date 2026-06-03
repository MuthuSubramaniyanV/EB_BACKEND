import re
from fastapi import UploadFile

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


def extract_text_from_filename(filename: str) -> tuple[float, float]:
    digits = re.findall(r"\d+", filename)
    if not digits:
        return 0.0, 0.0
    reading = float(digits[0])
    confidence = 0.96 if len(digits) > 1 else 0.88
    return reading, confidence


async def perform_ocr(file: UploadFile) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported file type for OCR")

    reading, confidence = extract_text_from_filename(file.filename)
    return {"reading": reading, "confidence": confidence}
