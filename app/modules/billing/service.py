from fastapi import HTTPException
from sqlmodel import Session
from app.modules.billing.model import Bill
from app.modules.billing.repository import BillRepository
from app.modules.readings.repository import ReadingRepository


DEFAULT_TARIFF_PER_UNIT = 5.0


class BillingService:
    @staticmethod
    def generate_bill(session: Session, user_id: int, month: str, gst: float, fixed_charge: float, additional_charge: float, generated_by: int) -> Bill:
        readings = ReadingRepository.list_by_user(session, user_id)
        if len(readings) < 2:
            raise HTTPException(status_code=400, detail="Not enough readings to generate a bill")

        sorted_readings = sorted(readings, key=lambda r: r.created_at)
        start_reading = sorted_readings[-2].reading_value
        end_reading = sorted_readings[-1].reading_value
        units_consumed = max(0.0, end_reading - start_reading)
        tariff_amount = units_consumed * DEFAULT_TARIFF_PER_UNIT
        total_amount = tariff_amount + gst + fixed_charge + additional_charge

        bill = Bill(
            user_id=user_id,
            month=month,
            start_reading=start_reading,
            end_reading=end_reading,
            units_consumed=units_consumed,
            tariff_amount=tariff_amount,
            gst_amount=gst,
            fixed_charge=fixed_charge,
            additional_charge=additional_charge,
            total_amount=total_amount,
            status="draft",
            generated_by=generated_by,
        )
        return BillRepository.create(session, bill)

    @staticmethod
    def list_bills(session: Session, current_user) -> list[Bill]:
        if current_user.role == "admin":
            return BillRepository.list_all(session)
        return BillRepository.list_by_user(session, current_user.id)

    @staticmethod
    def get_bill(session: Session, current_user, bill_id: int) -> Bill:
        bill = BillRepository.get(session, bill_id)
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        if current_user.role != "admin" and bill.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        return bill

    @staticmethod
    def approve_bill(session: Session, bill_id: int, approved_by: int) -> Bill:
        bill = BillRepository.get(session, bill_id)
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        bill.status = "approved"
        bill.generated_by = approved_by
        return BillRepository.update(session, bill)
