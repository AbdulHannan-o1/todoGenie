from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON # Corrected import
from phase2.backend.src.models.base import BaseSQLModel

class TaskBase(SQLModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    status: str = Field(default="pending", regex="^(pending|completed|in progress|archived)$")
    priority: str = Field(regex="^(low|medium|high)$")
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON)) # Corrected usage
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = Field(default=None, regex="^(daily|weekly|monthly)$")

class Task(BaseSQLModel, TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)

    # user: Optional["User"] = Relationship(back_populates="tasks") # Assuming a User model exists

class TaskCreate(TaskBase):
    user_id: int

class TaskRead(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    status: Optional[str] = Field(default=None, regex="^(pending|completed|in progress|archived)$")
    priority: Optional[str] = Field(default=None, regex="^(low|medium|high)$")
    tags: Optional[List[str]] = Field(default=None)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = Field(default=None, regex="^(daily|weekly|monthly)$")
