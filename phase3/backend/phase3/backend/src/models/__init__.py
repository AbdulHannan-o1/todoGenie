# Import all models from their respective files to avoid duplicate definitions
from .conversation import Conversation
from .message import Message

# Import User and Task from the models.py file
from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4

# Define the models to avoid conflicts, without relationships to avoid circular import issues
class User(SQLModel, table=True):
    __tablename__ = "user"  # Explicitly set table name
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    status: str = "Active"  # Active, Suspended, Deleted

class Task(SQLModel, table=True):
    __tablename__ = "task"  # Explicitly set table name
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending")  # pending, in progress, completed, archived, cancelled
    priority: Optional[str] = None  # low, medium, high
    recurrence: Optional[str] = None  # daily, weekly, monthly, yearly
    due_date: Optional[datetime] = None
    tags: str = Field(default="")
    user_id: UUID = Field(foreign_key="user.id")
    # AI integration fields
    ai_generated: bool = Field(default=False)  # Whether the task was created via AI
    ai_intent: Optional[str] = Field(default=None)  # The intent detected by AI (e.g., "add_task", "update_task")
    ai_context_id: Optional[str] = Field(default=None)  # ID of the conversation context in which task was created

__all__ = ["User", "Task", "Conversation", "Message"]