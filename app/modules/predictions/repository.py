from typing import List, Optional
from sqlmodel import Session, select
from app.modules.predictions.model import Prediction


class PredictionRepository:
    @staticmethod
    def create(session: Session, prediction: Prediction) -> Prediction:
        session.add(prediction)
        session.commit()
        session.refresh(prediction)
        return prediction

    @staticmethod
    def list_by_user(session: Session, user_id: int) -> List[Prediction]:
        return session.exec(select(Prediction).where(Prediction.user_id == user_id)).all()

    @staticmethod
    def list_all(session: Session) -> List[Prediction]:
        return session.exec(select(Prediction)).all()
