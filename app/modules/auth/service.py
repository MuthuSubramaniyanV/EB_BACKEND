from fastapi import HTTPException
from app.core.security import hash_password, verify_password, create_access_token
from app.modules.users.model import User
from app.modules.auth.repository import AuthRepository


class AuthService:
    @staticmethod
    def register_user(
        session,
        name: str,
        email: str,
        password: str,
        role: str = "consumer",
        phone: str | None = None,
        consumer_number: str | None = None,
    ) -> User:
        existing = AuthRepository.get_by_email(session, email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        password_hash = hash_password(password)
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            phone=phone,
            consumer_number=consumer_number,
        )
        return AuthRepository.create_user(session, user)

    @staticmethod
    def authenticate_user(session, email: str, password: str, role: str) -> tuple[User, str]:
        user = AuthRepository.get_by_email(session, email)
        if not user or user.role != role or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email, password, or role")
        token = create_access_token(str(user.id), user.role)
        return user, token
