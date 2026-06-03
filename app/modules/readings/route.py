from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_user
from app.modules.readings.schema import ReadingCreate, ReadingUpdate, ReadingRead
from app.modules.readings.service import ReadingService
from app.modules.users.model import User

router = APIRouter(prefix="/readings")


@router.post("", response_model=ReadingRead)
def create_reading(
    payload: ReadingCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return ReadingService.create_reading(session, current_user, payload.dict(exclude_unset=True))


@router.get("", response_model=list[ReadingRead])
def list_readings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return ReadingService.list_readings(session, current_user)


@router.get("/{reading_id}", response_model=ReadingRead)
def get_reading(
    reading_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return ReadingService.get_reading(session, current_user, reading_id)


@router.put("/{reading_id}", response_model=ReadingRead)
def update_reading(
    reading_id: int,
    payload: ReadingUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return ReadingService.update_reading(session, current_user, reading_id, payload.dict(exclude_unset=True))
# - GET /
# - POST /
# - GET /{reading_id}
# - PUT /{reading_id}
