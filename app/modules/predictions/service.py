from datetime import datetime
from typing import List

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sqlmodel import Session
from fastapi import HTTPException

from app.modules.predictions.model import Prediction
from app.modules.predictions.repository import PredictionRepository
from app.modules.billing.repository import BillRepository
from app.modules.users.model import User


class PredictionService:
    @staticmethod
    def generate_prediction(session: Session, user_id: int, prediction_month: str) -> Prediction:
        bills = BillRepository.list_by_user(session, user_id)
        if not bills:
            raise HTTPException(status_code=404, detail="No bill history available for prediction")

        units = [bill.units_consumed for bill in bills]
        amounts = [bill.total_amount for bill in bills]

        if len(units) >= 3:
            X = np.arange(len(units)).reshape(-1, 1)
            units_model = RandomForestRegressor(random_state=42, n_estimators=50)
            amount_model = RandomForestRegressor(random_state=42, n_estimators=50)
            units_model.fit(X, np.array(units))
            amount_model.fit(X, np.array(amounts))
            next_index = np.array([[len(units)]])
            predicted_units = float(max(0.0, units_model.predict(next_index)[0]))
            predicted_bill = float(max(0.0, amount_model.predict(next_index)[0]))
        else:
            predicted_units = float(sum(units) / len(units))
            predicted_bill = float(sum(amounts) / len(amounts))

        prediction = Prediction(
            user_id=user_id,
            predicted_units=predicted_units,
            predicted_bill=predicted_bill,
            prediction_month=prediction_month,
        )
        return PredictionRepository.create(session, prediction)

    @staticmethod
    def list_predictions(session: Session, current_user: User, user_id: int) -> List[Prediction]:
        if current_user.role == "admin" or current_user.id == user_id:
            return PredictionRepository.list_by_user(session, user_id)
        raise HTTPException(status_code=403, detail="Not authorized")
