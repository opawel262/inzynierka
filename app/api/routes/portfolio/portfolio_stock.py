from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.utils import limiter
from app.core.config import settings


router = APIRouter(
    prefix="/portfolios/stocks",
    tags=["Portfolio Management - Stocks"],
)


@router.get("", deprecated=True)
def get_portfolio_stocks(db: Session = Depends(get_db)):
    pass


@router.post("", deprecated=True)
def create_portfolio_stock(db: Session = Depends(get_db)):
    pass


@router.delete("", deprecated=True)
def delete_all_portfolio_stocks(db: Session = Depends(get_db)):
    pass


@router.get("/{portfolio_id}", deprecated=True)
def get_detail_portfolio_stock(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.patch("/{portfolio_id}", deprecated=True)
def update_portfolio_stock(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.delete("/{portfolio_id}", deprecated=True)
def delete_portfolio_stock(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.post("/{portfolio_id}/watched_stocks/{symbol}", deprecated=True)
def add_watched_stock(portfolio_id: int, symbol: str, db: Session = Depends(get_db)):
    pass


@router.delete("/{portfolio_id}/watched_stocks/{symbol}", deprecated=True)
def remove_watched_stock(portfolio_id: int, symbol: str, db: Session = Depends(get_db)):
    pass


@router.delete("/{portfolio_id}/watched_stocks", deprecated=True)
def remove_all_watched_stocks(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.get("/{portfolio_id}/transactions", deprecated=True)
def get_portfolio_stock_transactions(portfolio_id: int, db: Session = Depends(get_db)):
    pass


@router.post("/{portfolio_id}/transactions", deprecated=True)
def create_portfolio_stock_transaction(
    portfolio_id: int, db: Session = Depends(get_db)
):
    pass


@router.get("/{portfolio_id}/transactions/{transaction_id}", deprecated=True)
def get_detail_portfolio_stock_transaction(
    portfolio_id: int, transaction_id: int, db: Session = Depends(get_db)
):
    pass


@router.patch("/{portfolio_id}/transactions/{transaction_id}", deprecated=True)
def update_portfolio_stock_transaction(
    portfolio_id: int, transaction_id: int, db: Session = Depends(get_db)
):
    pass


@router.delete("/{portfolio_id}/transactions/{transaction_id}", deprecated=True)
def delete_portfolio_stock_transaction(
    portfolio_id: int, transaction_id: int, db: Session = Depends(get_db)
):
    pass
