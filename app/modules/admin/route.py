from fastapi import APIRouter, Depends, Query
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import require_admin
from app.modules.admin.service import AdminService
from app.modules.admin.schema import ConsumerMonthImages, ApproveReadingPayload, ModifyReadingPayload, ConsumerSummary
from app.modules.users.model import User

router = APIRouter(prefix="/admin")


@router.get("/consumers", response_model=list[ConsumerSummary])
def list_consumers(
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return [
        ConsumerSummary(
            id=user.id,
            name=user.name,
            email=user.email,
            consumer_number=user.consumer_number,
        )
        for user in AdminService.list_consumers(session)
    ]


@router.get("/consumer/{consumer_id}/month-images", response_model=ConsumerMonthImages)
def consumer_month_images(
    consumer_id: int,
    month: str = Query(..., description="Month in YYYY-MM format"),
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return AdminService.get_consumer_month_images(session, consumer_id, month)


@router.post("/approve-reading")
def approve_reading(
    payload: ApproveReadingPayload,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return AdminService.approve_reading(session, payload.reading_id, _admin.id, payload.verification_note)


@router.post("/modify-reading")
def modify_reading(
    payload: ModifyReadingPayload,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return AdminService.modify_reading(session, payload.reading_id, payload.reading_value, payload.verification_note)
