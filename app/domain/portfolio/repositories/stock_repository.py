# gpw_repository.py
from app.domain.portfolio.models import Stock, StockHistoricalPrice
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime


def update_model(model: Stock, data: dict) -> Stock:
    for key, value in data.items():
        if hasattr(model, key):
            setattr(model, key, value)
    return model


class StockRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_stock(self, stock_data: Dict) -> Stock:
        stock = Stock(**stock_data)
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)

        return stock

    def get_all_stocks(self) -> List[Stock]:
        return self.db.query(Stock).order_by(Stock.market_cap_rank.asc()).all()

    def get_stock_by_name_or_symbol_alike(self, name_or_symbol: str) -> List[Stock]:
        return (
            self.db.query(Stock)
            .filter(
                Stock.name.ilike(f"%{name_or_symbol}%")
                | Stock.symbol.ilike(f"%{name_or_symbol}%")
            )
            .order_by(Stock.market_cap_rank.asc())
            .all()
        )

    def update_stock(self, update_data: Dict) -> Stock:
        existing_stock = self.get_stock_by_symbol(update_data["symbol"])
        if not existing_stock:
            raise ValueError(
                f"Stock with symbol {update_data['symbol']} does not exist."
            )
        for key, value in update_data.items():
            if value is None:
                continue
            setattr(existing_stock, key, value)

        self.db.commit()
        self.db.refresh(existing_stock)

        return existing_stock

    def get_stock_by_symbol(self, symbol: str) -> Stock | None:
        return self.db.query(Stock).filter(Stock.symbol == symbol).first()

    def create_stock_historical_price(self, stock: Stock, historical_price_data: Dict):
        historical_price = StockHistoricalPrice(**historical_price_data)
        stock.historical_prices.append(historical_price)
        self.db.add(historical_price)
        self.db.commit()
        self.db.refresh(historical_price)

        return historical_price

    def update_stock_historical_price(
        self, historical_price: StockHistoricalPrice, update_data: Dict
    ) -> StockHistoricalPrice:
        for key, value in update_data.items():
            setattr(historical_price, key, value)
        self.db.commit()
        self.db.refresh(historical_price)

        return historical_price

    def get_stock_historical_prices_by_symbol_period(
        self, symbol: str, period: str
    ) -> List[StockHistoricalPrice]:
        return (
            self.db.query(StockHistoricalPrice)
            .join(Stock)
            .filter(Stock.symbol == symbol, StockHistoricalPrice.period == period)
            .all()
        )

    def get_stock_historical_prices_by_symbol_period_date(
        self, symbol: str, period: str, date: str
    ) -> List[StockHistoricalPrice]:
        return (
            self.db.query(StockHistoricalPrice)
            .join(Stock)
            .filter(
                Stock.symbol == symbol,
                StockHistoricalPrice.date == date,
                StockHistoricalPrice.period == period,
            )
            .first()
        )

    def get_stock_historical_price_by_symbol_period_date(
        self, symbol: str, period: str, date: datetime
    ):
        return (
            self.db.query(StockHistoricalPrice)
            .join(Stock)
            .filter(
                Stock.symbol == symbol,
                StockHistoricalPrice.period == period,
                StockHistoricalPrice.date == date,
            )
            .first()
        )

    def get_stock_historical_prices_by_symbol_period(
        self, symbol: str, period: str
    ) -> List[StockHistoricalPrice]:
        return (
            self.db.query(StockHistoricalPrice)
            .join(Stock)
            .filter(
                Stock.symbol == symbol,
                StockHistoricalPrice.period == period,
            )
            .all()
        )

    def get_stock_historical_prices_by_symbol_period_from_to_date(
        self, symbol: str, period: str, from_date: datetime, to_date: datetime
    ) -> List[StockHistoricalPrice]:
        return (
            self.db.query(StockHistoricalPrice)
            .join(Stock)
            .filter(
                Stock.symbol == symbol,
                StockHistoricalPrice.period == period,
                StockHistoricalPrice.date >= from_date,
                StockHistoricalPrice.date <= to_date,
            )
            .all()
        )

    def get_stocks_biggest_market_cap(self, limit: int = 3) -> List[Stock] | None:
        return (
            self.db.query(Stock)
            .order_by(Stock.market_cap_rank.asc())
            .limit(limit)
            .all()
        )

    def get_stocks_by_name_or_symbol_alike(self, name_or_symbol: str) -> List[Stock]:
        return (
            self.db.query(Stock)
            .filter(
                Stock.name.ilike(f"%{name_or_symbol}%")
                | Stock.symbol.ilike(f"%{name_or_symbol}%")
            )
            .order_by(Stock.market_cap_rank.asc())
            .all()
        )

    def get_stocks_biggest_market_cap(self, limit: int = 3) -> List[Stock] | None:
        return self.db.query(Stock).order_by(Stock.market_cap.desc()).limit(limit).all()

    def get_stocks_biggest_gainers(self, limit: int = 3) -> List[Stock] | None:
        return (
            self.db.query(Stock)
            .order_by(Stock.price_change_percentage_24h.desc())
            .limit(limit)
            .all()
        )

    def get_stocks_biggest_losers(self, limit: int = 3) -> List[Stock] | None:
        return (
            self.db.query(Stock)
            .order_by(Stock.price_change_percentage_24h.asc())
            .limit(limit)
            .all()
        )
