from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import inspect, text
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

engine = None

if settings.DATABASE_URL:
    try:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
        )
        logger.info("Database engine created successfully")
    except Exception as e:
        logger.exception("Failed to create database engine: %s", e)
        engine = None


def create_db_and_tables():
    if not engine:
        raise RuntimeError("Database engine not initialized")
    SQLModel.metadata.create_all(engine)
    _ensure_users_app_state_column()


def _ensure_users_app_state_column():
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {col["name"] for col in inspector.get_columns("users")}
    if "app_state" not in existing_columns:
        with engine.begin() as conn:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN app_state TEXT")
            )


def get_session():
    if not engine:
        raise RuntimeError("DATABASE_URL not configured correctly")
    with Session(engine) as session:
        yield session
