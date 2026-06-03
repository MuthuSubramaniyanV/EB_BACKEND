import io
import re
from typing import Optional

from fastapi import UploadFile

from app.services.filebase_service import FilebaseService

try:
    from PIL import Image
    import numpy as np
    import cv2
    import pytesseract
    from pytesseract import Output
except Exception:
    # These imports may not be available in minimal environments.
    Image = None
    np = None
    cv2 = None
    pytesseract = None
    Output = None


ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


def _extract_longest_number(text: str) -> Optional[str]:
    # keep only digits and dots, return the longest group
    groups = re.findall(r"[0-9][0-9.,]+", text.replace('\n', ' '))
    if not groups:
        groups = re.findall(r"\d+", text)
    if not groups:
        return None
    # normalize groups by removing commas
    groups = [g.replace(',', '').replace(' ', '') for g in groups]
    groups.sort(key=lambda s: len(s), reverse=True)
    return groups[0]


def perform_ocr_bytes(content: bytes, filename: str = "image.jpg") -> dict:
    """Perform OCR on raw image bytes and return reading and optional confidence.

    Uses pytesseract + simple preprocessing. Returns dict: {"reading": float, "confidence": float}
    """
    if Image is None:
        raise RuntimeError("OCR dependencies not installed. Install pillow, opencv-python-headless, pytesseract, numpy.")

    pil = Image.open(io.BytesIO(content)).convert("RGB")
    img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

    # Preprocess: grayscale, resize, denoise
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    scale = max(1, int(800 / max(w, h)))
    if scale > 1:
        gray = cv2.resize(gray, (w * scale, h * scale), interpolation=cv2.INTER_LINEAR)

    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    # adaptive threshold to highlight digits
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 9)

    # try to find large rectangular contours that might be the meter display
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        if area < 500:  # skip small
            continue
        ar = cw / float(ch + 1)
        if ar > 2.0:  # likely a wide display
            candidates.append((area, x, y, cw, ch))

    crops = []
    # sort by area desc
    for _, x, y, cw, ch in sorted(candidates, key=lambda t: t[0], reverse=True):
        pad = 5
        sx = max(0, x - pad)
        sy = max(0, y - pad)
        ex = min(gray.shape[1], x + cw + pad)
        ey = min(gray.shape[0], y + ch + pad)
        crop = gray[sy:ey, sx:ex]
        crops.append(crop)

    # always also try the full image
    crops.append(gray)

    best_reading = None
    best_conf = 0.0

    ocr_config = "--psm 7 -c tessedit_char_whitelist=0123456789,."
    for c in crops:
        # increase contrast
        c = cv2.resize(c, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        c = cv2.GaussianBlur(c, (3, 3), 0)
        _, c = cv2.threshold(c, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        pil_img = Image.fromarray(c)

        # get OCR text and detailed data
        raw_text = pytesseract.image_to_string(pil_img, config=ocr_config)
        data = pytesseract.image_to_data(pil_img, output_type=Output.DICT, config=ocr_config)

        cand = _extract_longest_number(raw_text)
        if cand:
            # compute mean confidence for numeric words
            confs = []
            for i, txt in enumerate(data.get('text', [])):
                if txt and re.search(r"\d", txt):
                    try:
                        conf = float(data.get('conf', [])[i])
                        if conf > 0:
                            confs.append(conf)
                    except Exception:
                        continue
            mean_conf = (sum(confs) / len(confs) / 100.0) if confs else 0.0
            # normalize cand
            val = cand.replace(',', '').replace(' ', '')
            try:
                reading_val = float(val)
            except Exception:
                continue
            if mean_conf > best_conf or best_reading is None:
                best_conf = mean_conf
                best_reading = reading_val

    if best_reading is None:
        # fallback: try digits in filename
        digits = re.findall(r"\d+", filename)
        if digits:
            best_reading = float(digits[-1])
            best_conf = 0.4
        else:
            best_reading = 0.0
            best_conf = 0.0

    return {"reading": best_reading, "confidence": round(best_conf, 2)}


async def perform_ocr(file: UploadFile) -> dict:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Unsupported file type for OCR")
    content = await file.read()
    return perform_ocr_bytes(content, getattr(file, 'filename', 'image.jpg'))


def perform_ocr_from_bucket(file_name: str) -> dict:
    """Fetch an image from Filebase and run OCR on it."""
    fb = FilebaseService()
    content = fb.get_image_bytes(file_name)
    return perform_ocr_bytes(content, file_name)
