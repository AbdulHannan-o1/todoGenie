"""
Dependencies for chat endpoints using Better Auth integration
"""
from fastapi import Depends, HTTPException, status
from typing import Optional
from uuid import UUID

from src.auth import get_current_user, oauth2_scheme
from src.models import User
from src.db import get_session
from sqlmodel import Session, select


async def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get current user from JWT token with database verification
    """
    from src.auth import verify_token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id_str = verify_token(token, credentials_exception)

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    with next(get_session()) as session:
        user = session.get(User, user_id)
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