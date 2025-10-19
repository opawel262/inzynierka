from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from app.api.deps import get_db, authenticate
from app.core.utils import limiter
from fastapi.responses import StreamingResponse
from app.domain.portfolio.services.stock_portfolio_service import (
    StockPortfolioService,
)
from app.domain.portfolio.repositories.stock_portfolio_repository import (
    StockPortfolioRepository,
)
from app.domain.raport.services.raport_crypto_portfolio_service import (
    RaportCryptoPortfolioService,
)
from app.domain.raport.services.raport_stock_portfolio_service import (
    RaportStockPortfolioService,
)
from app.domain.portfolio.services.crypto_portfolio_service import (
    CryptoPortfolioService,
)

from app.domain.portfolio.repositories.crypto_portfolio_repository import (
    CryptoPortfolioRepository,
)
import os

router = APIRouter(
    prefix="/raport",
    tags=["Summaries raports"],
)


@router.post(
    "/stock-portfolio",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF report for stock portfolio",
        }
    },
)
def create_stock_portfolio(
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(authenticate),
):
    stock_portfolio_repository = StockPortfolioRepository(db)
    stock_portfolio_service = StockPortfolioService(stock_portfolio_repository, user_id)
    pdf_io = RaportStockPortfolioService(
        user_id=user_id, stock_portfolio_service=stock_portfolio_service
    ).generate_report_pdf()

    return StreamingResponse(
        pdf_io,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=raport_stock_portfolio.pdf"
        },
    )


@router.post(
    "/crypto-portfolio",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF report for crypto portfolio",
        }
    },
)
def create_crypto_portfolio(
    request: Request,
    db: Session = Depends(get_db),
    user_id: str = Depends(authenticate),
):
    crypto_portfolio_repository = CryptoPortfolioRepository(db)
    crypto_portfolio_service = CryptoPortfolioService(
        crypto_portfolio_repository, user_id
    )
    pdf_io = RaportCryptoPortfolioService(
        user_id=user_id, crypto_portfolio_service=crypto_portfolio_service
    ).generate_report_pdf()
    return StreamingResponse(
        pdf_io,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=raport_crypto_portfolio.pdf"
        },
    )
