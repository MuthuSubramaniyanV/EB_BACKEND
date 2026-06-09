import pytest
from urllib.error import URLError

from fastapi import HTTPException
from app.modules.meter.service import MeterCaptureService
from app.modules.uploads.model import MeterUpload


class DummyResponse:
    def __init__(self, status: int, content: bytes, headers: dict[str, str]):
        self.status = status
        self._content = content
        self._headers = headers

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def getheader(self, name: str, default=None):
        return self._headers.get(name, default)

    def read(self):
        return self._content


def test_capture_remote_image_success(monkeypatch):
    monkeypatch.setattr("app.modules.meter.service.settings.ESP32_CAMERA_URL", "http://camera/capture")

    def fake_urlopen(request, timeout):
        return DummyResponse(
            status=200,
            content=b"\xff\xd8\xff\xdb",
            headers={"Content-Type": "image/jpeg"},
        )

    monkeypatch.setattr("app.modules.meter.service.urlopen", fake_urlopen)
    monkeypatch.setattr(
        "app.modules.meter.service.filebase.upload_image",
        lambda content, file_name, content_type: f"https://bucket/{file_name}",
    )

    def fake_save(session, upload: MeterUpload):
        upload.id = 123
        return upload

    monkeypatch.setattr("app.modules.meter.service.UploadRepository.save", fake_save)

    upload = MeterCaptureService.capture_remote_image(None, user_id=7)

    assert upload.id == 123
    assert upload.user_id == 7
    assert upload.image_url.startswith("https://bucket/meter_")
    assert upload.status == "pending_ocr"


def test_capture_remote_image_unreachable(monkeypatch):
    monkeypatch.setattr("app.modules.meter.service.settings.ESP32_CAMERA_URL", "http://camera/capture")

    def fake_urlopen(request, timeout):
        raise URLError("Connection refused")

    monkeypatch.setattr("app.modules.meter.service.urlopen", fake_urlopen)

    with pytest.raises(HTTPException) as exc_info:
        MeterCaptureService.capture_remote_image(None, user_id=1)

    assert exc_info.value.status_code == 502
    assert "unreachable" in str(exc_info.value.detail).lower()
