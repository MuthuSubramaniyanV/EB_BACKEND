from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_user, require_admin
from app.modules.anomalies.schema import AnomalyCreate, AnomalyRead
from app.modules.anomalies.service import AnomalyService
from app.modules.users.model import User

router = APIRouter(prefix="/anomaly")


@router.post("/check", response_model=list[AnomalyRead])
def check_anomaly(
    payload: AnomalyCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return AnomalyService.check_anomalies(session, payload.user_id)


@router.get("/{user_id}", response_model=list[AnomalyRead])
def get_anomalies(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return AnomalyService.list_anomalies(session, current_user, user_id)
