from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1)
    description: Optional[str] = None
    status: str = Field(default="pending") # Enum: 'pending', 'in progress', 'completed', 'archived', 'cancelled'
    priority: Optional[str] = Field(default="medium") # Enum: 'low', 'medium', 'high'
    tags: Optional[List[str]] = Field(default_factory=list) # JSONB array in PostgreSQL
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None # Enum: 'daily', 'weekly', 'monthly'

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="tasks")