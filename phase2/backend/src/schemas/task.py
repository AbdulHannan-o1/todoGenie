from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    tags: Optional[str] = None
    recurrence: Optional[str] = None

class TaskCreate(TaskBase):
    user_id: UUID
    status: str = "pending"

class TaskRead(TaskBase):
    id: UUID
    status: str
    user_id: UUID

    class Config:
        orm_mode = True

class TaskUpdate(TaskBase):
    status: Optional[str] = None

class ReminderCreate(BaseModel):
    reminder_date: datetime
