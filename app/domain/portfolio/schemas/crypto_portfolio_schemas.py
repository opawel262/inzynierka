from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from app.domain.portfolio.schemas.crypto_schemas import CryptoSymbolSchema


class CryptoPortfolioCreateTransaction(BaseModel):
    description: str
    transaction_type: str
    amount: float
    price_per_unit: float
    transaction_date: datetime
    crypto: CryptoSymbolSchema


class CryptoPortfolioUpdateTransaction(BaseModel):
    description: Optional[str] = None
    transaction_type: Optional[str] = None
    amount: Optional[float] = None
    price_per_unit: Optional[float] = None
    transaction_date: Optional[datetime] = None
    crypto: Optional[CryptoSymbolSchema] = None


class CryptoPortfolioTransactions(BaseModel):
    id: UUID
    transaction_type: Literal["buy", "sell"]
    amount: float
    price_per_unit: float
    transaction_date: datetime
    crypto: CryptoSymbolSchema


class CryptoPortfolioTransactionDetail(CryptoPortfolioTransactions):
    description: Optional[str] = None


class CryptoPortfolioWatched(BaseModel):
    id: int
    crypto: CryptoSymbolSchema


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


class CryptoPortfolioDetailSchema(CryptoPortfolioSchema):
    crypto_transactions: list[CryptoPortfolioTransactions]
    watched_cryptos: list[CryptoPortfolioWatched]
