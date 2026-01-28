from typing import List, Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
from pydantic import BaseModel
from .message import Message  # This will be handled differently in alembic


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
    # Note: For alembic, we'll use string reference to avoid circular imports
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)


# Pydantic models for API requests/responses
class ConversationCreate(BaseModel):
    title: Optional[str] = "New Conversation"
    user_id: UUID


class MessageCreate(BaseModel):
    conversation_id: UUID
    content: str
    role: str = "user"
    message_type: str = "text"


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int