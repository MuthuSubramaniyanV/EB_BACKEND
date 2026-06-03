from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from typing import Optional, Generator
from app.core.security import decode_token
from app.core.database import get_session
from app.modules.users.model import User
from app.modules.auth.repository import AuthRepository
from app.core import database

bearer = HTTPBearer()


def optional_session() -> Generator[Optional[Session], None, None]:
    """Dependency that yields a DB session or None when no engine configured."""
    if not database.engine:
        yield None
        return
    yield from get_session()


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    session: Optional[Session] = Depends(optional_session),
) -> User:
    try:
        payload = decode_token(creds.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("no sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    # If DB session available, use it; otherwise use in-memory auth repository
    if session is not None:
        user = session.exec(select(User).where(User.id == user_id)).first()
    else:
        user = AuthRepository.get(None, int(user_id))

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    return user
