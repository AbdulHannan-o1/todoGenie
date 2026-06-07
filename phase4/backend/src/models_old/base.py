from datetime import datetime, UTC
from typing import Optional
from sqlmodel import Field, SQLModel

class BaseSQLModel(SQLModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)