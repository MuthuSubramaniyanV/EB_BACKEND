from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_user, require_admin
from app.modules.payments.schema import PaymentCreate, PaymentRead, PaymentVerify
from app.modules.payments.service import PaymentService
from app.modules.users.model import User

router = APIRouter(prefix="/payments")


@router.post("/upload-receipt", response_model=PaymentRead)
def upload_receipt(
    payload: PaymentCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PaymentRead:
    return PaymentService.create_payment(session, payload.bill_id, str(payload.receipt_url), current_user.id)


@router.get("", response_model=list[PaymentRead])
def list_payments(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return PaymentService.list_payments(session, current_user)


@router.put("/{payment_id}/verify", response_model=PaymentRead)
def verify_payment(
    payment_id: int,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return PaymentService.verify_payment(session, payment_id, _admin.id)
