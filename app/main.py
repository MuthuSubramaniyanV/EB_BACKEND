from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import create_db_and_tables

from app.modules.auth.route import router as auth_router
from app.modules.users.route import router as users_router
from app.modules.devices.route import router as devices_router
from app.modules.uploads.route import router as uploads_router
from app.modules.readings.route import router as readings_router
from app.modules.billing.route import router as billing_router
from app.modules.payments.route import router as payments_router
from app.modules.predictions.route import router as prediction_router
from app.modules.anomalies.route import router as anomaly_router
from app.modules.ocr.route import router as ocr_router
from app.modules.admin.route import router as admin_router
from app.modules.state.route import router as state_router
from app.modules.meter.route import router as meter_router
from app.modules.users.model import User
from app.modules.readings.model import MeterReading
from app.modules.billing.model import Bill
from app.core.security import hash_password

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="MeterX Backend API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_demo_users()
    seed_demo_data()


def seed_demo_users():
    from sqlmodel import Session, select
    from app.core.database import engine

    if engine is None:
        return

    with Session(engine) as session:
        existing_admin = session.exec(select(User).where(User.role == "admin")).first()
        if not existing_admin:
            session.add(
                User(
                    name="KSEB Admin",
                    email="admin@meterx.com",
                    password_hash=hash_password("admin"),
                    role="admin",
                )
            )

        existing_consumer = session.exec(select(User).where(User.email == "consumer@meterx.com")).first()
        if not existing_consumer:
            session.add(
                User(
                    name="Anjali Nair",
                    email="consumer@meterx.com",
                    password_hash=hash_password("1234"),
                    role="consumer",
                    consumer_number="C10239",
                )
            )

        session.commit()


def seed_demo_data():
    from sqlmodel import Session, select
    from app.core.database import engine

    if engine is None:
        return

    with Session(engine) as session:
        consumer = session.exec(select(User).where(User.email == "consumer@meterx.com")).first()
        admin = session.exec(select(User).where(User.email == "admin@meterx.com")).first()

        if consumer:
            existing_reading = session.exec(select(MeterReading).where(MeterReading.user_id == consumer.id)).first()
            if not existing_reading:
                base_time = datetime.utcnow()
                session.add(
                    MeterReading(
                        user_id=consumer.id,
                        reading_value=1467.0,
                        ocr_confidence=0.96,
                        verified=False,
                        created_at=base_time - timedelta(days=30),
                    )
                )
                session.add(
                    MeterReading(
                        user_id=consumer.id,
                        reading_value=1538.0,
                        ocr_confidence=0.94,
                        verified=False,
                        created_at=base_time,
                    )
                )

        if consumer and admin:
            existing_bill = session.exec(
                select(Bill)
                .where(Bill.user_id == consumer.id)
                .where(Bill.month == "2024-06")
            ).first()
            if not existing_bill:
                session.add(
                    Bill(
                        user_id=consumer.id,
                        month="2024-06",
                        start_reading=1467.0,
                        end_reading=1538.0,
                        units_consumed=71.0,
                        tariff_amount=355.0,
                        gst_amount=35.5,
                        fixed_charge=50.0,
                        additional_charge=10.0,
                        total_amount=450.5,
                        status="draft",
                        generated_by=admin.id,
                    )
                )

        session.commit()


@app.get("/health")
def health():
    return {"ok": True}


# =========================
# API ROUTES
# =========================

app.include_router(auth_router, tags=["Authentication"])

app.include_router(users_router, tags=["Users"])

app.include_router(devices_router, tags=["Devices"])

app.include_router(uploads_router, tags=["Uploads"])

app.include_router(readings_router, tags=["Readings"])

app.include_router(billing_router, tags=["Billing"])

app.include_router(payments_router, tags=["Payments"])

app.include_router(prediction_router, tags=["Predictions"])

app.include_router(anomaly_router, tags=["Anomalies"])

app.include_router(ocr_router, tags=["OCR"])
app.include_router(meter_router, tags=["Meter"])

app.include_router(admin_router, tags=["Admin"])

app.include_router(state_router, tags=["State"])


# =========================
# FRONTEND
# MUST BE LAST
# =========================

app.mount(
    "/",
    StaticFiles(
        directory=BASE_DIR,
        html=True
    ),
    name="frontend"
)