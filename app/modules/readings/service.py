from fastapi import HTTPException
from sqlmodel import Session
from app.modules.readings.model import MeterReading
from app.modules.readings.repository import ReadingRepository


class ReadingService:
    @staticmethod
    def create_reading(session: Session, current_user, payload: dict) -> MeterReading:
        user_id = payload.get("user_id") or current_user.id
        if current_user.role != "admin" and user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to create reading for another user")

        reading = MeterReading(
            user_id=user_id,
            upload_id=payload.get("upload_id"),
            reading_value=payload["reading_value"],
            ocr_confidence=payload.get("ocr_confidence", 0.0),
        )
        return ReadingRepository.create(session, reading)

    @staticmethod
    def list_readings(session: Session, current_user) -> list[MeterReading]:
        if current_user.role == "admin":
            return ReadingRepository.list_all(session)
        return ReadingRepository.list_by_user(session, current_user.id)

    @staticmethod
    def get_reading(session: Session, current_user, reading_id: int) -> MeterReading:
        reading = ReadingRepository.get(session, reading_id)
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")
        if current_user.role != "admin" and reading.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        return reading

    @staticmethod
    def update_reading(session: Session, current_user, reading_id: int, payload: dict) -> MeterReading:
        reading = ReadingRepository.get(session, reading_id)
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")
        if current_user.role != "admin" and reading.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        for field, value in payload.items():
            if value is None:
                continue
            setattr(reading, field, value)
        return ReadingRepository.update(session, reading)
