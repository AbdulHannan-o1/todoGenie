from typing import List, Optional
from datetime import datetime, UTC
from pydantic import field_validator # Import field_validator
from sqlmodel import Field, SQLModel

class TaskBase(SQLModel):
    title: str = Field(min_length=1)
    description: Optional[str] = None
    status: str = Field(default="pending") # Enum: 'pending', 'in progress', 'completed', 'archived', 'cancelled'
    priority: Optional[str] = Field(default="medium") # Enum: 'low', 'medium', 'high'
    tags: Optional[List[str]] = Field(default_factory=list)
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None # Enum: 'daily', 'weekly', 'monthly'

    @field_validator('due_date', mode='after')
    def validate_due_date(cls, v):
        if v:
            # If v is offset-naive, assume UTC
            if v.tzinfo is None:
                v = v.replace(tzinfo=UTC)
            if v < datetime.now(UTC):
                raise ValueError('due_date must be in the future')
        return v

    @field_validator('recurrence', mode='after')
    def validate_recurrence(cls, v):
        if v and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('recurrence must be one of "daily", "weekly", or "monthly"')
        return v

class TaskCreate(TaskBase):
    user_id: int

class ReminderCreate(SQLModel):
    reminder_date: datetime

    @field_validator('reminder_date', mode='after')
    def validate_reminder_date(cls, v):
        if v:
            # If v is offset-naive, assume UTC
            if v.tzinfo is None:
                v = v.replace(tzinfo=UTC)
            if v < datetime.now(UTC):
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

    @field_validator('due_date', mode='after')
    def validate_due_date(cls, v):
        if v:
            # If v is offset-naive, assume UTC
            if v.tzinfo is None:
                v = v.replace(tzinfo=UTC)
            if v < datetime.now(UTC):
                raise ValueError('due_date must be in the future')
        return v

    @field_validator('recurrence', mode='after')
    def validate_recurrence(cls, v):
        if v and v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('recurrence must be one of "daily", "weekly", or "monthly"')
        return v
