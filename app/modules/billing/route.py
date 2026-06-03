from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_user, require_admin
from app.modules.billing.schema import BillCreate, BillRead
from app.modules.billing.service import BillingService
from app.modules.users.model import User

router = APIRouter(prefix="/bills")


@router.post("/generate", response_model=BillRead)
def generate_bill(
    payload: BillCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return BillingService.generate_bill(
        session,
        payload.user_id,
        payload.month,
        payload.gst,
        payload.fixed_charge,
        payload.additional_charge,
        generated_by=_admin.id,
    )


@router.get("", response_model=list[BillRead])
def list_bills(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return BillingService.list_bills(session, current_user)


@router.get("/{bill_id}", response_model=BillRead)
def get_bill(
    bill_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return BillingService.get_bill(session, current_user, bill_id)


@router.post("/{bill_id}/approve", response_model=BillRead)
def approve_bill(
    bill_id: int,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return BillingService.approve_bill(session, bill_id, _admin.id)
