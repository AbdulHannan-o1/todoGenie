"""
Consolidated models file for Alembic migrations
This file combines all models to avoid import issues during migration generation
"""
from typing import List, Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel


# User model (from original models.py)
class User(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    status: str = Field(default="Active")  # Active, Suspended, Deleted

    tasks: List["Task"] = Relationship(back_populates="owner")


# Task model (from original models.py with AI extensions)
class Task(SQLModel, table=True):
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

    owner: User = Relationship(back_populates="tasks")


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