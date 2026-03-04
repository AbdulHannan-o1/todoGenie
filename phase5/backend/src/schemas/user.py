from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    username: str

from pydantic import Field
class UserCreate(UserBase):
    password: str = Field(min_length=8)

from pydantic import ConfigDict

class UserRead(UserBase):
    id: UUID
    status: str

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None