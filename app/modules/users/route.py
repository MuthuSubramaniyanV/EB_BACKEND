from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.core.database import get_session
from app.core.deps import get_current_user, require_admin
from app.modules.users.service import UserService
from app.modules.users.schema import UserRead, UserUpdate
from app.modules.users.model import User

router = APIRouter(prefix="/users")


@router.get("", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    _admin: User = Depends(require_admin),
):
    return UserService.list_all_users(session)


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return UserService.get_user(session, user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = UserService.get_user(session, user_id)
    if current_user.role != "admin" and payload.role is not None:
        raise HTTPException(status_code=403, detail="Cannot change role")
    return UserService.update_user(session, user, payload.dict(exclude_unset=True))


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    user = UserService.get_user(session, user_id)
    UserService.delete_user(session, user)
    return {"detail": "User deleted"}
