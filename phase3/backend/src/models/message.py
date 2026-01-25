from typing import Optional
from datetime import datetime, UTC
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel


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