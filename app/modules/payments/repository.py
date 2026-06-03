from typing import List, Optional
from sqlmodel import Session, select
from app.modules.payments.model import Payment
from app.modules.billing.model import Bill


class PaymentRepository:
    @staticmethod
    def create(session: Session, payment: Payment) -> Payment:
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment

    @staticmethod
    def get(session: Session, payment_id: int) -> Optional[Payment]:
        return session.exec(select(Payment).where(Payment.id == payment_id)).first()

    @staticmethod
    def list_by_user(session: Session, user_id: int) -> List[Payment]:
        return session.exec(
            select(Payment)
            .join(Bill, Bill.id == Payment.bill_id)
            .where(Bill.user_id == user_id)
        ).all()

    @staticmethod
    def list_all(session: Session) -> List[Payment]:
        return session.exec(select(Payment)).all()

    @staticmethod
    def save(session: Session, payment: Payment) -> Payment:
        session.add(payment)
        session.commit()
        session.refresh(payment)
        return payment
