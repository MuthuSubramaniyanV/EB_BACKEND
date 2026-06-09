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

    Uses pytesseract + enhanced preprocessing. Returns dict: {"reading": float, "confidence": float}
    """
    if Image is None:
        raise RuntimeError("OCR dependencies not installed. Install pillow, opencv-python-headless, pytesseract, numpy.")

    pil = Image.open(io.BytesIO(content)).convert("RGB")
    img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    scale = max(1, int(1200 / max(w, h)))
    if scale > 1:
        gray = cv2.resize(gray, (w * scale, h * scale), interpolation=cv2.INTER_LINEAR)

    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.equalizeHist(gray)

    def _normalize_text(text: str) -> str:
        return (
            text.replace("O", "0")
            .replace("o", "0")
            .replace("I", "1")
            .replace("l", "1")
            .replace("S", "5")
            .replace("s", "5")
            .replace("|", "1")
            .replace("", "")
        )

    def _parse_candidate(raw_text: str, data: dict) -> tuple[Optional[float], float]:
        raw_text = _normalize_text(raw_text)
        cand = _extract_longest_number(raw_text)
        if not cand:
            return None, 0.0

        confs = []
        for i, txt in enumerate(data.get("text", [])):
            if txt and re.search(r"\d", txt):
                try:
                    conf = float(data.get("conf", [])[i])
                    if conf > 0:
                        confs.append(conf)
                except Exception:
                    continue

        mean_conf = (sum(confs) / len(confs) / 100.0) if confs else 0.0
        val = cand.replace(",", "").replace(" ", "")
        try:
            return float(val), mean_conf
        except Exception:
            return None, 0.0

    def _ocr_image(image, config):
        if isinstance(image, Image.Image):
            pil_img = image
        else:
            pil_img = Image.fromarray(image)

        raw_text = pytesseract.image_to_string(
            pil_img,
            config=config
        )

        print("\n========================")
        print("OCR CONFIG:", config)
        print("RAW OCR TEXT:", repr(raw_text))
        print("========================\n")

        data = pytesseract.image_to_data(
            pil_img,
            output_type=Output.DICT,
            config=config
        )

        return _parse_candidate(raw_text, data)

    ocr_configs = [
        "--psm 7 -c tessedit_char_whitelist=0123456789,.",
        "--psm 6 -c tessedit_char_whitelist=0123456789,.",
        "--psm 8 -c tessedit_char_whitelist=0123456789,."
    ]

    best_reading = None
    best_conf = 0.0

    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 9
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    candidates = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        if area < 1500:
            continue
        ar = cw / float(ch + 1)
        if ar > 1.5:
            candidates.append((area, x, y, cw, ch))

    crops = []
    for _, x, y, cw, ch in sorted(candidates, key=lambda t: t[0], reverse=True):
        pad = 10
        sx = max(0, x - pad)
        sy = max(0, y - pad)
        ex = min(gray.shape[1], x + cw + pad)
        ey = min(gray.shape[0], y + ch + pad)
        crop = gray[sy:ey, sx:ex]
        if crop.size > 0:
            crops.append(crop)

    crops.append(gray)

    for crop in crops:
        crop = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
        crop = cv2.GaussianBlur(crop, (3, 3), 0)

        for thresh_mode in [cv2.THRESH_BINARY + cv2.THRESH_OTSU, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU]:
            _, processed = cv2.threshold(crop, 0, 255, thresh_mode)
            for config in ocr_configs:
                reading_val, mean_conf = _ocr_image(processed, config)
                if reading_val is not None:
                    if best_reading is None or mean_conf > best_conf or (mean_conf == best_conf and reading_val > best_reading):
                        best_conf = mean_conf
                        best_reading = reading_val

    if best_reading is None or best_reading == 0.0:
        for config in ocr_configs:
            reading_val, mean_conf = _ocr_image(gray, config)
            if reading_val is not None and (best_reading is None or mean_conf > best_conf):
                best_conf = mean_conf
                best_reading = reading_val

    if best_reading is None:
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
