from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)

    tasks: List["Task"] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user_id: UUID = Field(foreign_key="user.id")
    owner: Optional[User] = Relationship(back_populates="tasks")

# Schemas for authentication
class Token(SQLModel):
    access_token: str
    token_type: str

class UserRead(SQLModel):
    id: UUID
    email: str
    is_active: bool

class UserCreate(SQLModel):
    email: str
    password: str

class UserLogin(SQLModel):
    email: str
    password: str

# Schemas for tasks
class TaskCreate(SQLModel):
    title: str
    description: Optional[str] = None

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None