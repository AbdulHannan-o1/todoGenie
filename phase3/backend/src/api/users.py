from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from ..db.session import get_session
from ..models import User
from ..schemas.user import UserRead
from .auth import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=List[UserRead])
def read_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all users.
    """
    users = session.query(User).all()
    return users

@router.get("/me", response_model=UserRead)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the current user's information.
    """
    return current_user

@router.get("/{user_id}", response_model=UserRead)
def read_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a user by ID.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user