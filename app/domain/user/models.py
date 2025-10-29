from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime

from app.core.config import settings
from app.domain.model_base import Base


class User(Base):

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.timezone("Europe/Warsaw", func.now()),
    )
    is_active = Column(Boolean, default=False, nullable=False)
    username = Column(String, nullable=False, unique=True)
    avatar_image = Column(String, default=settings.DEFAULT_USER_AVATAR_IMAGE_URL)

    budgets = relationship(
        "Budget", back_populates="owner", cascade="all, delete-orphan"
    )
    stock_portfolios = relationship("StockPortfolio", back_populates="owner")
    crypto_portfolios = relationship("CryptoPortfolio", back_populates="owner")


class Token(Base):
    __tablename__ = "tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    value = Column(String, nullable=False, unique=True)
    token_for = Column(String, nullable=False)
    expiration_time = Column(DateTime, nullable=False)
