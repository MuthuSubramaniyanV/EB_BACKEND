from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

if not settings.DATABASE_URL:
    # You can still run locally without DB for early testing,
    # but for real usage set DATABASE_URL in .env / Render env vars.
    engine = None
else:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def create_db_and_tables():
    if engine:
        SQLModel.metadata.create_all(engine)


def get_session():
    if not engine:
        raise RuntimeError("DATABASE_URL not set. Add it to .env or Render env vars.")
    with Session(engine) as session:
        yield session
