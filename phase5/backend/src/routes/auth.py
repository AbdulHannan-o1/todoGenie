from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from phase2.backend.src.db import get_session
from phase2.backend.src.services.auth_service import authenticate_user, create_user_access_token
from phase2.backend.src.auth import ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from datetime import timedelta
from phase2.backend.src.models import User

router = APIRouter()

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_user_access_token(user, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(current_user: User = Depends(get_current_user)):
    # For stateless JWTs, logout typically means the client discards the token.
    # No server-side action is strictly necessary unless a token blacklist is implemented.
    return {"message": "Successfully logged out"}
