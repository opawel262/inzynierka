from typing import List
from sqlalchemy.orm import Session
from app.core.database import SessionLocal

from app.domain.portfolio.repositories.gpw_stock_repository import GPWStockRepository
from app.domain.portfolio.services.gpw_stock_service import GPWStockService
from app.domain.portfolio.fetchers.stock_gpw_fetcher import GPWStockFetcher

from app.celery_app import celery_app


@celery_app.task(name="app.tasks.fetch_gpw_data_by_tickers")
def fetch_gpw_data_by_tickers(tickers: List[str]) -> None:
    db: Session = SessionLocal()
    try:
        stock_repository = GPWStockRepository(db_session=db)
        stock_service = GPWStockService(
            fetcher=GPWStockFetcher(tickers=tickers), repository=stock_repository
        )
        stock_service.fetch_and_save_stock_data()
    finally:
        db.close()
