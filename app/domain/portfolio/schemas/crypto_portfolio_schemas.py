from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class CryptoPortfolioCreateSchema(BaseModel):
    title: str
    is_public: bool = False
    description: Optional[str] = None
    color: str


class CryptoPortfolioSchema(CryptoPortfolioCreateSchema):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime


class CryptoPortfolioUpdateSchema(CryptoPortfolioCreateSchema):
    title: Optional[str] = None
    is_public: Optional[bool] = None
    color: Optional[str] = None
