from typing import List, Optional
from sqlmodel import Session, select
from app.modules.users.model import User


class UserRepository:
    @staticmethod
    def get(session: Session, user_id: int) -> Optional[User]:
        return session.exec(select(User).where(User.id == user_id)).first()

    @staticmethod
    def get_by_email(session: Session, email: str) -> Optional[User]:
        return session.exec(select(User).where(User.email == email)).first()

    @staticmethod
    def list_users(session: Session) -> List[User]:
        return session.exec(select(User)).all()

    @staticmethod
    def create(session: Session, user: User) -> User:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def update(session: Session, user: User) -> User:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    @staticmethod
    def delete(session: Session, user: User) -> None:
        session.delete(user)
        session.commit()
