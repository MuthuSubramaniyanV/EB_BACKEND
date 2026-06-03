from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_user, require_admin
from app.modules.predictions.schema import PredictionCreate, PredictionRead
from app.modules.predictions.service import PredictionService
from app.modules.users.model import User

router = APIRouter(prefix="/prediction")


@router.post("/generate", response_model=PredictionRead)
def generate_prediction(
    payload: PredictionCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
) -> PredictionRead:
    return PredictionService.generate_prediction(session, payload.user_id, payload.prediction_month)


@router.get("/{user_id}", response_model=list[PredictionRead])
def get_predictions(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[PredictionRead]:
    return PredictionService.list_predictions(session, current_user, user_id)
