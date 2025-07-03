# gpw_repository.py
from app.domain.portfolio.models import Stock, StockHistoricalPrice
from sqlalchemy.orm import Session


class GPWStockRepository:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_stock(self, stock: Stock):
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)

        return stock

    def get_all_stocks(self):
        return self.db.query(Stock).all()

    def get_stock_by_ticker(self, ticker: str):
        return self.db.query(Stock).filter(Stock.ticker == ticker).first()
