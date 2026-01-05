from typing import Optional, List
from datetime import datetime, UTC
from sqlmodel import Field, SQLModel, Relationship, JSON, Column

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1)
    description: Optional[str] = None
    status: str = Field(default="pending") # Enum: 'pending', 'in progress', 'completed', 'archived', 'cancelled'
    priority: Optional[str] = Field(default="medium") # Enum: 'low', 'medium', 'high'
    tags: Optional[List[str]] = Field(default_factory=list, sa_column=Column(JSON)) # JSONB array in PostgreSQL
    due_date: Optional[datetime] = None
    recurrence: Optional[str] = None # Enum: 'daily', 'weekly', 'monthly'
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="tasks")