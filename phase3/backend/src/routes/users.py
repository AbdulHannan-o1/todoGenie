from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from phase2.backend.src.models import User
from phase2.backend.src.db.session import get_session
from phase2.backend.src.services.user_service import create_user, get_user_by_email, get_user_by_username
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserRegister, session: Session = Depends(get_session)):
    if get_user_by_email(session, user_data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    if get_user_by_username(session, user_data.username):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    user = create_user(session, user_data.email, user_data.username, user_data.password)
    return user