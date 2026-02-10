from sqlmodel import SQLModel, create_engine, Session
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


def get_session():
    if not engine:
        raise RuntimeError("DATABASE_URL not configured correctly")
    with Session(engine) as session:
        yield session
