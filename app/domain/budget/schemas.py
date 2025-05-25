from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.domain.user.schemas import UserPublic


class BudgetSchema(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    is_public: bool
    owner: UserPublic
    description: Optional[str] = None
    color: str


class BudgetDetailSchema(BudgetSchema):
    transactions: Optional[list] = None


class BudgetCreateSchema(BaseModel):
    title: str
    is_public: bool = False
    description: Optional[str] = None
    color: str


class BudgetUpdateSchema(BudgetCreateSchema):
    pass
