from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
import sqlalchemy as sa


class Tag(SQLModel, table=True):
    __tablename__ = "tag"  # Explicitly set table name
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    name: str = Field(max_length=50)
    color: Optional[str] = Field(max_length=7, default=None)  # hex color code
    created_at: datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    updated_at: datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP")))


class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tag"  # Junction table for many-to-many relationship
    task_id: UUID = Field(foreign_key="task.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True)


class Event(SQLModel, table=True):
    __tablename__ = "event"  # Explicitly set table name
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    task_id: Optional[UUID] = Field(default=None, foreign_key="task.id")
    event_type: str = Field(max_length=50)  # created, updated, completed, deleted, reminder_sent
    event_data: Optional[dict] = Field(default=None, sa_column=sa.Column(sa.JSON))  # payload specific to event type
    created_at: datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    processed: bool = Field(default=False)


class Notification(SQLModel, table=True):
    __tablename__ = "notification"  # Explicitly set table name
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    task_id: Optional[UUID] = Field(default=None, foreign_key="task.id")
    type: str = Field(max_length=50)  # reminder, recurring_task_created, system_alert
    message: str
    scheduled_time: datetime
    sent_time: Optional[datetime] = None
    status: str = Field(default="scheduled", max_length=20)  # scheduled, sent, failed, cancelled
    created_at: datetime = Field(sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))