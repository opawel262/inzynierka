from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from app.domain.portfolio.schemas.stock_schemas import StockSymbolSchema
from typing import Any


class StockBaseSchema(StockSymbolSchema):
    name: Optional[str] = None
    price: Optional[float] = None
    price_change_percentage_24h: Optional[float] = None


class StockPortfolioCreateTransaction(BaseModel):
    description: str
    transaction_type: str
    amount: float
    price_per_unit: float
    transaction_date: datetime
    stock: StockSymbolSchema


class StockPortfolioUpdateTransaction(BaseModel):
    description: Optional[str] = None
    transaction_type: Optional[str] = None
    amount: Optional[float] = None
    price_per_unit: Optional[float] = None
    transaction_date: Optional[datetime] = None
    stock: Optional[StockSymbolSchema] = None


class StockPortfolioTransactions(BaseModel):
    id: UUID
    transaction_type: str
    amount: float
    price_per_unit: float
    transaction_date: datetime
    stock: StockBaseSchema
    profit_loss: Optional[float] = None
    profit_loss_percentage: Optional[float] = None
    description: Optional[str] = None


class StockPortfolioTransactionDetail(StockPortfolioTransactions):
    pass


class StockPortfolioWatched(BaseModel):
    id: int
    stock: StockBaseSchema
    percentage_profit_loss_24h: Optional[float] = None
    profit_loss_24h: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percentage: Optional[float] = None
    total_invested: Optional[float] = None
    avg_buy_price: Optional[float] = None
    holdings: Optional[float] = None
    current_value: Optional[float] = None


class StockPortfolioCreateSchema(BaseModel):
    title: str
    is_public: bool = False
    description: Optional[str] = None
    color: str


class StockPortfolioSchema(StockPortfolioCreateSchema):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    total_watched_stocks: int
    total_transactions: int
    total_investment: float
    profit_loss: Optional[float] = None
    profit_loss_percentage: Optional[float] = None
    total_investment: Optional[float] = None
    profit_loss_24h: Optional[float] = None
    percentage_profit_loss_24h: Optional[float] = None

    current_value: Optional[float] = None


class StockPortfolioUpdateSchema(StockPortfolioCreateSchema):
    title: Optional[str] = None
    is_public: Optional[bool] = None
    color: Optional[str] = None


class StockPortfolioDetailSchema(StockPortfolioSchema):
    watched_stocks: list[StockPortfolioWatched]
    stocks_percentage_holdings: Optional[dict[str, float]] = None
    historical_value_7d: Optional[list[dict[str, Any]]] = None
    historical_value_1m: Optional[list[dict[str, Any]]] = None
    historical_value_1y: Optional[list[dict[str, Any]]] = None
