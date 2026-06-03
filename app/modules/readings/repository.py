from typing import List, Optional
from sqlmodel import Session, select
from app.modules.readings.model import MeterReading


class ReadingRepository:
    @staticmethod
    def create(session: Session, reading: MeterReading) -> MeterReading:
        session.add(reading)
        session.commit()
        session.refresh(reading)
        return reading

    @staticmethod
    def get(session: Session, reading_id: int) -> Optional[MeterReading]:
        return session.exec(select(MeterReading).where(MeterReading.id == reading_id)).first()

    @staticmethod
    def list_by_user(session: Session, user_id: int) -> List[MeterReading]:
        return session.exec(select(MeterReading).where(MeterReading.user_id == user_id)).all()

    @staticmethod
    def list_all(session: Session) -> List[MeterReading]:
        return session.exec(select(MeterReading)).all()

    @staticmethod
    def update(session: Session, reading: MeterReading) -> MeterReading:
        session.add(reading)
        session.commit()
        session.refresh(reading)
        return reading
