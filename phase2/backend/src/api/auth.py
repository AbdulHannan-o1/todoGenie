from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session

from ..db.session import get_session
from ..services.user_service import get_user_by_email
from ..services.auth_service import create_user_access_token, authenticate_user
from ..schemas.auth import Token
from ..schemas.user import UserCreate, UserRead
from ..services.user_service import create_user as create_user_service
from ..models import User
from ..auth import get_current_user, get_password_hash
from ..utils.hash import verify_password
from ..config import settings

def create_auth_router() -> APIRouter:
    router = APIRouter(prefix="/api/auth", tags=["auth"])

    @router.post("/register", response_model=UserRead)
    def register_user(user_create: UserCreate, session: Session = Depends(get_session)):
        """
        Register a new user.
        """
        return create_user_service(session=session, email=user_create.email, username=user_create.username, password=user_create.password)

    @router.post("/token", response_model=Token)
    def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
        """
        Login for access token.
        """
        user = authenticate_user(session=session, identifier=form_data.username, password=form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_user_access_token(
            user=user, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    
    return router

router = create_auth_router()
