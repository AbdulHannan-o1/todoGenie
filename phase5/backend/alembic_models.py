"""
Consolidated models file for Alembic migrations
This file combines all models to avoid import issues during migration generation
"""
from typing import List, Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
import sqlalchemy as sa


# User model (from original models.py)
class User(SQLModel, table=True):
    __tablename__ = "user"  # Explicitly set table name
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    status: str = "Active"  # Active, Suspended, Deleted


# Task model (from original models.py with AI extensions)
class Task(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    title: str
    description: Optional[str] = None
    status: str = Field(default="pending")  # pending, in progress, completed, archived, cancelled
    priority: str = Field(default="medium")  # low, medium, high, urgent
    recurrence_pattern: Optional[dict] = Field(default=None, sa_column=sa.Column(sa.Text))  # Text field for recurrence rules (JSON stored as text)
    due_date: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))
    reminder_time: Optional[datetime] = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=True))
    tags: str = Field(default="")  # Will store comma-separated tag IDs or names
    parent_task_id: Optional[UUID] = Field(default=None, foreign_key="task.id")  # For hierarchical tasks
    user_id: UUID = Field(foreign_key="user.id")
    # AI integration fields
    ai_generated: bool = Field(default=False)  # Whether the task was created via AI
    ai_intent: Optional[str] = Field(default=None)  # The intent detected by AI (e.g., "add_task", "update_task")
    ai_context_id: Optional[str] = Field(default=None)  # ID of the conversation context in which task was created
    # Timestamp fields
    created_at: datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    updated_at: datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP")))

    # Note: Relationship definitions are simplified for migration compatibility
    # owner: User = Relationship(back_populates="tasks")


# Message model (from separate message.py)
class Message(SQLModel, table=True):
    """
    Model for storing individual messages in a conversation
    """
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id")
    user_id: UUID = Field(foreign_key="user.id")
    role: str = Field(default="user")  # "user" or "assistant"
    content: str
    message_type: str = Field(default="text")  # "text", "voice"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationship back to conversation
    conversation: "Conversation" = Relationship(back_populates="messages")


# Conversation model (from separate conversation.py)
class Conversation(SQLModel, table=True):
    """
    Model for storing conversation data
    """
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    title: str = Field(default="New Conversation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationship to messages in this conversation
    messages: List[Message] = Relationship(back_populates="conversation", cascade_delete=True)