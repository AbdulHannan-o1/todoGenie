from typing import Optional
from uuid import UUID
from sqlmodel import Session
from phase2.backend.src.db.session import get_session
from phase2.backend.src.models import User
from phase2.backend.src.schemas.user import UserCreate
from phase2.backend.src.utils.hash import get_password_hash

def create_user(session: Session, email: str, username: str, password: str) -> User:
    hashed_password = get_password_hash(password)
    user = User(email=email, username=username, hashed_password=hashed_password, status="Active")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.query(User).filter(User.email == email).first()

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.query(User).filter(User.username == username).first()

def update_user_status(session: Session, user_id: UUID, new_status: str) -> Optional[User]:
    user = session.get(User, user_id)
    if not user:
        return None
    user.status = new_status
    session.add(user)
    session.commit()
    session.refresh(user)
    return user