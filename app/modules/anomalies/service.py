from typing import List

import numpy as np
from sklearn.ensemble import IsolationForest
from sqlmodel import Session
from fastapi import HTTPException

from app.modules.anomalies.model import Anomaly
from app.modules.anomalies.repository import AnomalyRepository
from app.modules.readings.repository import ReadingRepository
from app.modules.users.model import User


class AnomalyService:
    @staticmethod
    def check_anomalies(session: Session, user_id: int) -> List[Anomaly]:
        readings = ReadingRepository.list_by_user(session, user_id)
        if len(readings) < 4:
            raise HTTPException(status_code=400, detail="Not enough readings for anomaly detection")

        values = np.array([[reading.reading_value] for reading in readings])
        model = IsolationForest(random_state=42, contamination=0.2)
        model.fit(values)
        predictions = model.predict(values)
        anomalies = []
        for idx, reading in enumerate(readings):
            if predictions[idx] == -1:
                score = float(model.decision_function([values[idx]])[0])
                severity = "high" if score < -0.5 else "medium" if score < -0.1 else "low"
                anomaly = Anomaly(
                    user_id=user_id,
                    reading_id=reading.id,
                    anomaly_type="spike",
                    description=f"Outlier reading {reading.reading_value} detected",
                    severity=severity,
                )
                anomalies.append(AnomalyRepository.create(session, anomaly))
        return anomalies

    @staticmethod
    def list_anomalies(session: Session, current_user: User, user_id: int):
        if current_user.role == "admin" or current_user.id == user_id:
            return AnomalyRepository.list_by_user(session, user_id)
        raise HTTPException(status_code=403, detail="Not authorized")
