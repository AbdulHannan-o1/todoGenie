from typing import List, Optional
from datetime import datetime
from pydantic import validator
from sqlmodel import Field, SQLModel

class TaskBase(SQLModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    status: str = Field(default="pending") # Enum: 'pending', 'in progress', 'completed', 'archived', 'cancelled'
    priority: Optional[str] = Field(default="medium") # Enum: 'low', 'medium', 'high'
    tags: Optional[List[str]] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None # Enum: 'daily', 'weekly', 'monthly'

    @validator('due_date')
    def due_date_must_be_in_the_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('due_date must be in the future')
        return v

    @validator('recurrence')
    def recurrence_must_be_valid(cls, v):
        if v and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('recurrence must be one of "daily", "weekly", or "monthly"')
        return v

class ReminderCreate(SQLModel):
    reminder_date: datetime

    @validator('reminder_date')
    def reminder_date_must_be_in_the_future(cls, v):
        if v < datetime.now():
            raise ValueError('reminder_date must be in the future')
        return v

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(min_length=1)
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None

    @validator('due_date')
    def due_date_must_be_in_the_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('due_date must be in the future')
        return v

    @validator('recurrence')
    def recurrence_must_be_valid(cls, v):
        if v and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('recurrence must be one of "daily", "weekly", or "monthly"')
        return v
