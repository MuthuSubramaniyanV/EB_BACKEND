from typing import List, Optional
from sqlmodel import Session, select
from app.modules.uploads.model import MeterUpload
from app.services.filebase_service import FilebaseService

filebase = FilebaseService()


class UploadRepository:
    @staticmethod
    def save(session: Session, upload: MeterUpload) -> MeterUpload:
        session.add(upload)
        session.commit()
        session.refresh(upload)
        return upload

    @staticmethod
    def get(session: Session, upload_id: int) -> Optional[MeterUpload]:
        return session.exec(select(MeterUpload).where(MeterUpload.id == upload_id)).first()

    @staticmethod
    def list_by_user(session: Session, user_id: int) -> List[MeterUpload]:
        return session.exec(select(MeterUpload).where(MeterUpload.user_id == user_id)).all()

    @staticmethod
    def list_all(session: Session) -> List[MeterUpload]:
        return session.exec(select(MeterUpload)).all()

    @staticmethod
    def delete(session: Session, upload: MeterUpload) -> None:
        session.delete(upload)
        session.commit()
