from fastapi import FastAPI
from app.core.database import create_db_and_tables

from app.modules.auth.route import router as auth_router
from app.modules.users.route import router as users_router
from app.modules.consumers.route import router as consumers_router
from app.modules.devices.route import router as devices_router
from app.modules.uploads.route import router as uploads_router
from app.modules.readings.route import router as readings_router
from app.modules.billing.route import router as billing_router
from app.modules.admin.route import router as admin_router

app = FastAPI(title="EB")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/health")
def health():
    return {"ok": True}


app.include_router(auth_router, tags=["auth"])
app.include_router(users_router,  tags=["users"])
app.include_router(consumers_router, tags=["consumers"])
app.include_router(devices_router,  tags=["devices"])
app.include_router(uploads_router, tags=["uploads"])
app.include_router(readings_router,  tags=["readings"])
app.include_router(billing_router,  tags=["billing"])
app.include_router(admin_router,  tags=["admin"])
