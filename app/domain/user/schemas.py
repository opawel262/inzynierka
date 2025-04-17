from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.core.config import settings


class Email(BaseModel):
    email: str


class PasswordUser(BaseModel):
    password: str


class AvatarImageUser(BaseModel):
    avatar_image: str

    @field_serializer("avatar_image")
    def serialize_avatar(self, value: str, _info) -> str:
        return value if value.startswith("http") else f"{settings.BACKEND_URL}{value}"


class NewPassword(BaseModel):
    new_password: str


class ResetPasswordUser(PasswordUser, NewPassword):
    pass


class UserUpdate(BaseModel):
    username: Optional[str] = None


class UserCreate(UserUpdate, PasswordUser):
    email: str

    class Config:
        from_attributes = True


class UserRetrieve(UserUpdate, AvatarImageUser):
    id: UUID
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
