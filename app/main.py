from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import create_db_and_tables

from app.modules.auth.route import router as auth_router
from app.modules.users.route import router as users_router
from app.modules.consumers.route import router as consumers_router
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


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "MeterX Backend Running"
    }


# =========================
# API ROUTES
# =========================

app.include_router(auth_router, tags=["Authentication"])

app.include_router(users_router, tags=["Users"])

app.include_router(consumers_router, tags=["Consumers"])

app.include_router(devices_router, tags=["Devices"])

app.include_router(uploads_router, tags=["Uploads"])

app.include_router(readings_router, tags=["Readings"])

app.include_router(billing_router, tags=["Billing"])

app.include_router(payments_router, tags=["Payments"])

app.include_router(prediction_router, tags=["Predictions"])

app.include_router(anomaly_router, tags=["Anomalies"])

app.include_router(ocr_router, tags=["OCR"])

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