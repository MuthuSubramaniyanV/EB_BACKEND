from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_user
from app.modules.auth.schema import UserRegister, UserLogin, AuthTokens, UserRead
from app.modules.auth.service import AuthService
from app.modules.users.model import User

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserRead)
def register_user(payload: UserRegister, session: Session = Depends(get_session)) -> User:
    return AuthService.register_user(
        session,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
        phone=payload.phone,
        consumer_number=payload.consumer_number,
    )


@router.post("/login", response_model=AuthTokens)
def login(payload: UserLogin, session: Session = Depends(get_session)) -> AuthTokens:
    user, token = AuthService.authenticate_user(session, payload.email, payload.password, payload.role)
    return AuthTokens(access_token=token, role=user.role, user_id=user.id)


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
