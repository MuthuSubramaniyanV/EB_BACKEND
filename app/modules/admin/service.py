from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from app.modules.users.repository import UserRepository
from app.modules.uploads.repository import UploadRepository
from app.modules.readings.repository import ReadingRepository
from app.modules.billing.service import BillingService


class AdminService:
    @staticmethod
    def list_consumers(session):
        return [user for user in UserRepository.list_users(session) if user.role == "consumer"]

    @staticmethod
    def get_consumer_month_images(session, consumer_id: int, month: str) -> dict:
        uploads = UploadRepository.list_by_user(session, consumer_id)
        target_uploads = [u for u in uploads if u.timestamp.strftime("%Y-%m") == month]
        if not target_uploads:
            return {
                "first_day_image": None,
                "last_day_image": None,
                "first_reading": None,
                "last_reading": None,
            }

        sorted_uploads = sorted(target_uploads, key=lambda u: u.timestamp)
        readings = ReadingRepository.list_by_user(session, consumer_id)
        month_readings = [r for r in readings if r.created_at.strftime("%Y-%m") == month]
        first_reading = month_readings[0].reading_value if month_readings else None
        last_reading = month_readings[-1].reading_value if month_readings else None
        return {
            "first_day_image": sorted_uploads[0].image_url,
            "last_day_image": sorted_uploads[-1].image_url,
            "first_reading": first_reading,
            "last_reading": last_reading,
        }

    @staticmethod
    def approve_reading(session, reading_id: int, admin_user_id: int, verification_note: Optional[str] = None):
        reading = ReadingRepository.get(session, reading_id)
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")
        reading.verified = True
        reading.verified_by = admin_user_id
        if verification_note:
            reading.verification_note = verification_note
        return ReadingRepository.update(session, reading)

    @staticmethod
    def modify_reading(session, reading_id: int, reading_value: float, verification_note: Optional[str] = None):
        reading = ReadingRepository.get(session, reading_id)
        if not reading:
            raise HTTPException(status_code=404, detail="Reading not found")
        reading.reading_value = reading_value
        if verification_note:
            reading.verification_note = verification_note
        reading.verified = True
        return ReadingRepository.update(session, reading)
