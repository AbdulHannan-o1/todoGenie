from typing import Optional
from sqlmodel import SQLModel

class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    role: str = "user"
