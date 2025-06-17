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
    title = Column(String(64), nullable=False)
    description = Column(String(255), nullable=True)
    color = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.timezone("UTC", func.now()))
    updated_at = Column(
        DateTime,
        server_default=func.timezone("UTC", func.now()),
        onupdate=func.timezone("UTC", func.now()),
    )
    is_public = Column(Boolean, default=False, nullable=False)
    owner_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    owner = relationship("User", back_populates="budgets")
    transactions = relationship(
        "BudgetTransaction", back_populates="budget", cascade="all, delete-orphan"
    )

    @property
    def total_amount(self) -> float:
        if len(self.transactions) == 0:
            return 0.0

        return sum(
            -t.amount if t.transaction_type == "-" else t.amount
            for t in self.transactions
        )


class BudgetTransaction(Base):
    __tablename__ = "budget_transactions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True)
    title = Column(String(64), nullable=False)
    budget_id = Column(
        UUID(as_uuid=True), ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False
    )
    transaction_type = Column(String(10), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
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
