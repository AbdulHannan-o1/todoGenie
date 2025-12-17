from typing import Optional
from sqlmodel import Session
from phase2.backend.src.db.session import get_session
from phase2.backend.src.models import User
from phase2.backend.src.config import settings
from phase2.backend.src.services.user_service import get_user_by_email, get_user_by_username
from phase2.backend.src.auth import verify_password, create_access_token
from datetime import timedelta

def authenticate_user(session: Session, identifier: str, password: str) -> Optional[User]:
    user = get_user_by_email(session, identifier)
    if not user:
        user = get_user_by_username(session, identifier)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    data = {"sub": user.username}
    return create_access_token(data=data, expires_delta=expires_delta)
