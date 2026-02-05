from typing import Optional
from uuid import UUID
from sqlmodel import Session, select
from ..db.session import get_session
from ..models import User
from ..schemas.user import UserCreate
from ..utils.hash import get_password_hash

def create_user(session: Session, email: str, username: str, password: str) -> User:
    hashed_password = get_password_hash(password)
    user = User(email=email, username=username, hashed_password=hashed_password, status="Active")
    session.add(user)
    try:
        # Flush to get server-generated values like ID
        session.flush()

        # Get the user ID before expunging (in case it's needed)
        user_id = user.id

        # Expunge immediately to detach from session before commit to avoid lazy loading issues
        session.expunge(user)

        # Commit the transaction
        session.commit()

        # Return the fully detached user object
        return user
    except Exception as e:
        session.rollback()
        # Check if it's a duplicate key error
        from sqlalchemy.exc import IntegrityError
        if isinstance(e, IntegrityError):
            from fastapi import HTTPException
            import logging
            logging.exception("Database integrity error during user creation")
            # Check which constraint was violated
            if 'ix_user_username' in str(e) or 'username' in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Username already registered"
                )
            elif 'ix_user_email' in str(e) or 'email' in str(e):
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="User already exists"
                )
        else:
            # Re-raise other exceptions
            raise

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def update_user_status(session: Session, user_id: UUID, new_status: str) -> Optional[User]:
    user = session.get(User, user_id)
    if not user:
        return None
    user.status = new_status
    session.add(user)
    session.commit()
    session.refresh(user)
    return user