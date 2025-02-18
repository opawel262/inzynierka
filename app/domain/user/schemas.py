from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.core.config import settings


class Email(BaseModel):
    email: str


class NewPassword(BaseModel):
    new_password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None


class UserCreate(UserUpdate):
    email: str
    password: str

    class Config:
        from_attributes = True


class UserRetrieve(UserUpdate):
    id: UUID
    email: EmailStr
    created_at: datetime
    avatar_image: str

    class Config:
        from_attributes = True

    @field_serializer("avatar_image")
    def serialize_avatar(self, value: str, _info) -> str:
        return value if value.startswith("http") else f"{settings.BACKEND_URL}{value}"
