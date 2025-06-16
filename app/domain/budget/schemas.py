from pydantic import BaseModel, Field
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime
from app.domain.user.schemas import UserPublic


class BudgetTransactionCategorySchema(BaseModel):
    id: int
    name: str
    icon: str


class BudgetTransactionCategoryDetailSchema(BudgetTransactionCategorySchema):
    pass


class BudgetTransactionSchema(BaseModel):
    title: str
    transaction_type: Literal["+", "-"]
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None


class BudgetTransactionCreateSchema(BudgetTransactionSchema):
    category_id: Optional[int] = None


class BudgetTransactionUpdateSchema(BudgetTransactionSchema):
    title: Optional[str] = None
    transaction_type: Optional[Literal["+", "-"]] = None
    amount: Optional[float] = None
    category_id: Optional[int] = None


class BudgetTransactionDetailSchema(BudgetTransactionSchema):
    id: UUID
    created_at: datetime
    updated_at: datetime
    budget_id: UUID
    category: Optional[BudgetTransactionCategoryDetailSchema] = None


class BudgetSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    is_public: bool
    owner: UserPublic
    description: Optional[str] = None
    color: str
    total_amount: float


class BudgetDetailSchema(BudgetSchema):
    transactions: Optional[list[BudgetTransactionSchema]] = None


class BudgetCreateSchema(BaseModel):
    title: str
    is_public: bool = False
    description: Optional[str] = None
    color: str


class BudgetUpdateSchema(BudgetCreateSchema):
    pass
