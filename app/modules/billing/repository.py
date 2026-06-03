from typing import List, Optional
from sqlmodel import Session, select
from app.modules.billing.model import Bill


class BillRepository:
    @staticmethod
    def create(session: Session, bill: Bill) -> Bill:
        session.add(bill)
        session.commit()
        session.refresh(bill)
        return bill

    @staticmethod
    def get(session: Session, bill_id: int) -> Optional[Bill]:
        return session.exec(select(Bill).where(Bill.id == bill_id)).first()

    @staticmethod
    def list_by_user(session: Session, user_id: int) -> List[Bill]:
        return session.exec(select(Bill).where(Bill.user_id == user_id)).all()

    @staticmethod
    def list_all(session: Session) -> List[Bill]:
        return session.exec(select(Bill)).all()

    @staticmethod
    def update(session: Session, bill: Bill) -> Bill:
        session.add(bill)
        session.commit()
        session.refresh(bill)
        return bill
