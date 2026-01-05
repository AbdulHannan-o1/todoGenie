from fastapi import Depends, HTTPException, status, Header
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

from src.config import SECRET_KEY, ALGORITHM

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

def get_current_user(authorization: str = Header(...)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(email=email, user_id=user_id)
    except JWTError:
        raise credentials_exception
    return token_data
