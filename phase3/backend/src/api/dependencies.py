"""
Dependencies for chat endpoints using Better Auth integration
"""
from fastapi import Depends, HTTPException, status

from src.auth import get_current_user, oauth2_scheme
from src.models import User
from src.db.session import get_session
from src.services.user_service import get_user_by_email
from src.config import settings
from jose import JWTError, jwt
from sqlmodel import Session, select


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    """
    Get current user from JWT token with database verification
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # First try to get user by email (as stored in the token)
    user = get_user_by_email(session, email)
    if user is None:
        # If not found by email, try to get by username (fallback)
        from src.services.user_service import get_user_by_username
        user = get_user_by_username(session, email)

    if user is None:
        raise credentials_exception
    if user.status != "Active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    return user


def get_current_active_user(current_user: User = Depends(get_current_user_from_token)) -> User:
    """
    Get current active user with additional checks
    """
    if current_user.status != "Active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    return current_user


# Dependency for chat endpoints that require authentication
CurrentUser = Depends(get_current_active_user)