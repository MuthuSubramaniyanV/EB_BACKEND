from fastapi import HTTPException
from app.modules.users.model import User
from app.modules.users.repository import UserRepository
from app.core.security import hash_password


class UserService:
    @staticmethod
    def list_all_users(session):
        return UserRepository.list_users(session)

    @staticmethod
    def get_user(session, user_id: int) -> User:
        user = UserRepository.get(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def update_user(session, target_user: User, update_data: dict) -> User:
        for key, value in update_data.items():
            if value is None:
                continue
            if key == "role" and target_user.role == "admin" and value not in {"admin", "consumer"}:
                continue
            setattr(target_user, key, value)
        return UserRepository.update(session, target_user)

    @staticmethod
    def delete_user(session, user: User) -> None:
        UserRepository.delete(session, user)
