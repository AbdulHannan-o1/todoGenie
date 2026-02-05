# Import all models from their respective files to avoid duplicate definitions
from .conversation import Conversation
from .message import Message
from .tags import Tag, TaskTag, Event, Notification

# Import User and Task from the models.py file
from sqlmodel import Field, SQLModel
import sqlalchemy as sa
from typing import Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4
import sqlalchemy as sa

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
    priority: str = Field(default="medium")  # low, medium, high, urgent
    recurrence_pattern: Optional[dict] = Field(default=None, sa_column=sa.Column(sa.Text))
    due_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))
    reminder_time: Optional[datetime] = Field(default=None, sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))
    tags: str = Field(default="")  # Will store comma-separated tag IDs or names
    parent_task_id: Optional[UUID] = Field(default=None, foreign_key="task.id")  # For hierarchical tasks
    user_id: UUID = Field(foreign_key="user.id")
    # AI integration fields
    ai_generated: bool = Field(default=False)  # Whether the task was created via AI
    ai_intent: Optional[str] = Field(default=None)  # The intent detected by AI (e.g., "add_task", "update_task")
    ai_context_id: Optional[str] = Field(default=None)  # ID of the conversation context in which task was created
    # Timestamp fields
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP")))

# Define UserLogin, TaskCreate, and TaskUpdate as Pydantic models (not tables, just for request validation)
from pydantic import BaseModel

class UserLogin(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    priority: Optional[str] = "medium"
    recurrence_pattern: Optional[dict] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    tags: Optional[str] = ""
    parent_task_id: Optional[UUID] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    recurrence_pattern: Optional[dict] = None
    due_date: Optional[datetime] = None
    reminder_time: Optional[datetime] = None
    tags: Optional[str] = None
    parent_task_id: Optional[UUID] = None

__all__ = ["User", "Task", "Conversation", "Message", "Tag", "TaskTag", "Event", "Notification", "UserLogin", "TaskCreate", "TaskUpdate"]