from sqlmodel import Session, select
from fastapi import HTTPException
from app.modules.payments.model import Payment
from app.modules.payments.repository import PaymentRepository
from app.modules.billing.repository import BillRepository
from app.modules.billing.model import Bill


class PaymentService:
    @staticmethod
    def create_payment(session: Session, bill_id: int, receipt_url: str, user_id: int) -> Payment:
        bill = BillRepository.get(session, bill_id)
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        if bill.user_id != user_id:
            raise HTTPException(status_code=403, detail="Cannot upload receipt for another user")

        payment = Payment(bill_id=bill_id, receipt_url=receipt_url)
        return PaymentRepository.create(session, payment)

    @staticmethod
    def list_payments(session: Session, current_user, user_id: int | None = None):
        if current_user.role == "admin":
            return PaymentRepository.list_all(session)
        return PaymentRepository.list_by_user(session, current_user.id)

    @staticmethod
    def verify_payment(session: Session, payment_id: int, admin_user_id: int) -> Payment:
        payment = PaymentRepository.get(session, payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        payment.payment_status = "verified"
        payment.verified_by = admin_user_id
        return PaymentRepository.save(session, payment)
