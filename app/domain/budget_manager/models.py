from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from uuid import uuid4
from datetime import datetime

from app.domain.model_base import Base


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    created_at = Column(DateTime, server_default=func.timezone("UTC", func.now()))
    updated_at = Column(
        DateTime,
        server_default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
    )
    is_public = Column(Boolean, default=False, nullable=False)
    creator_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    creator = relationship("User", back_populates="budgets")
    transactions = relationship("BudgetTransaction", back_populates="budget")


class BudgetTransaction(Base):
    __tablename__ = "budget_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    budget_id = Column(
        UUID(as_uuid=True), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False
    )
    transaction_type = Column(String, nullable=False)  # "dochod" or "przychod"
    amount = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at = Column(DateTime, server_default=func.timezone("UTC", func.now()))
    updated_at = Column(
        DateTime,
        server_default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
    )

    budget = relationship("Budget", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    icon = Column(String, nullable=True)

    transactions = relationship("BudgetTransaction", back_populates="category")
