from typing import List
from sqlmodel import Session, select
from app.modules.anomalies.model import Anomaly


class AnomalyRepository:
    @staticmethod
    def create(session: Session, anomaly: Anomaly) -> Anomaly:
        session.add(anomaly)
        session.commit()
        session.refresh(anomaly)
        return anomaly

    @staticmethod
    def list_by_user(session: Session, user_id: int) -> List[Anomaly]:
        return session.exec(select(Anomaly).where(Anomaly.user_id == user_id)).all()

    @staticmethod
    def list_all(session: Session) -> List[Anomaly]:
        return session.exec(select(Anomaly)).all()
