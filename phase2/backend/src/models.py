from typing import List, Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel

class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    status: str = Field(default="Active") # Active, Suspended, Deleted

    tasks: List["Task"] = Relationship(back_populates="owner")

class Task(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending") # pending, in progress, completed, archived, cancelled
    priority: Optional[str] = None # low, medium, high
    recurrence: Optional[str] = None # daily, weekly, monthly, yearly
    due_date: Optional[datetime] = None
    tags: str = Field(default="")
    user_id: UUID = Field(foreign_key="user.id")

    owner: User = Relationship(back_populates="tasks")
