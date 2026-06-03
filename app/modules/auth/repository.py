from typing import Optional
from sqlmodel import Session, select
from app.modules.users.model import User
from app.core import database


# Simple in-memory fallback store when a real DB isn't available (dev/demo)
_IN_MEMORY_USERS: dict[int, User] = {}
_ID_COUNTER = 1000


class AuthRepository:
    @staticmethod
    def _use_db() -> bool:
        return database.engine is not None

    @staticmethod
    def get_by_email(session: Optional[Session], email: str) -> Optional[User]:
        if AuthRepository._use_db():
            return session.exec(select(User).where(User.email == email)).first()
        # in-memory
        for u in _IN_MEMORY_USERS.values():
            if u.email == email:
                return u
        return None

    @staticmethod
    def get(session: Optional[Session], user_id: int) -> Optional[User]:
        if AuthRepository._use_db():
            return session.exec(select(User).where(User.id == user_id)).first()
        return _IN_MEMORY_USERS.get(int(user_id))

    @staticmethod
    def create_user(session: Optional[Session], user: User) -> User:
        if AuthRepository._use_db():
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        # assign an integer id for in-memory user
        global _ID_COUNTER
        _ID_COUNTER += 1
        user.id = _ID_COUNTER
        _IN_MEMORY_USERS[user.id] = user
        return user
