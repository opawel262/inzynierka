from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from datetime import datetime

from app.domain.model_base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)


class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    value = Column(String, nullable=False, unique=True)
    token_for = Column(String, nullable=False)
    expiration_time = Column(DateTime, nullable=False)
