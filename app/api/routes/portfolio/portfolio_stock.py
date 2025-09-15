from fastapi import APIRouter, HTTPException, status, Depends, Request, Path
from typing import Annotated
from sqlalchemy.orm import Session
from app.api.deps import get_db, authenticate
from app.core.utils import limiter
from app.core.exceptions import UnauthorizedError, NotFoundError, BadRequestError
from app.domain.portfolio.services.stock_portfolio_service import (
    StockPortfolioService,
)
from app.domain.portfolio.services.stock_service import StockService
from app.domain.portfolio.repositories.stock_repository import StockRepository
from app.domain.portfolio.repositories.stock_portfolio_repository import (
    StockPortfolioRepository,
)
from fastapi_pagination import Page, paginate
from uuid import UUID
from app.domain.portfolio.schemas.stock_portfolio_schemas import (
    StockPortfolioCreateSchema,
    StockPortfolioSchema,
    StockPortfolioUpdateSchema,
    StockPortfolioDetailSchema,
    StockPortfolioWatched,
    StockPortfolioTransactions,
    StockPortfolioTransactionDetail,
    StockPortfolioCreateTransaction,
    StockPortfolioUpdateTransaction,
)

router = APIRouter(
    prefix="/portfolios/stocks",
    tags=["Portfolio Management - Stocks"],
)


@router.get(
    "",
)
@limiter.limit("5/second")
def get_portfolio_stocks(
    request: Request,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> Page[StockPortfolioSchema]:
    stock_portfolio_repository = StockPortfolioRepository(db)
    stock_portfolio_service = StockPortfolioService(stock_portfolio_repository, user_id)
    stock_portfolios = stock_portfolio_service.get_all_portfolios()
    return paginate(stock_portfolios)


@router.post("")
@limiter.limit("1/second")
def create_portfolio_stock(
    request: Request,
    create_data: StockPortfolioCreateSchema,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> StockPortfolioSchema:
    stock_portfolio_repository = StockPortfolioRepository(db)
    stock_portfolio_service = StockPortfolioService(stock_portfolio_repository, user_id)
    stock_portfolio = stock_portfolio_service.create_portfolio(create_data.model_dump())
    return stock_portfolio


@router.delete("")
@limiter.limit("1/second")
def delete_all_portfolio_stocks(
    request: Request, db: Session = Depends(get_db), user_id=Depends(authenticate)
):
    stock_portfolio_repository = StockPortfolioRepository(db)
    stock_portfolio_service = StockPortfolioService(stock_portfolio_repository, user_id)

    is_success = stock_portfolio_service.delete_all_portfolios()

    return {
        "detail": (
            "Usunięto wszystkie portfele"
            if is_success
            else "Brak portfeli do usunięcia"
        )
    }


@router.get("/summary")
@limiter.limit("5/second")
def get_portfolio_stocks_summary(
    request: Request,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> dict:
    stock_portfolio_repository = StockPortfolioRepository(db)
    stock_portfolio_service = StockPortfolioService(stock_portfolio_repository, user_id)
    summary = stock_portfolio_service.get_portfolios_summary()
    return summary


@router.get("/{portfolio_id}")
@limiter.limit("5/second")
def get_detail_portfolio_stock(
    request: Request,
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(authenticate),
) -> StockPortfolioDetailSchema:
    stock_portfolio_repository = StockPortfolioRepository(db)
    stock_portfolio_service = StockPortfolioService(stock_portfolio_repository, user_id)
    try:
        stock_portfolio = stock_portfolio_service.get_portfolio_by_id(str(portfolio_id))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return stock_portfolio


@router.patch("/{portfolio_id}")
@limiter.limit("1/second")
def update_portfolio_stock(
    request: Request,
    portfolio_id: UUID,
    update_data: StockPortfolioUpdateSchema,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> StockPortfolioSchema:
    stock_portfolio_repository = StockPortfolioRepository(db)
    stock_portfolio_service = StockPortfolioService(stock_portfolio_repository, user_id)
    try:
        stock_portfolio = stock_portfolio_service.update_portfolio(
            str(portfolio_id), update_data.model_dump()
        )
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return stock_portfolio


@router.delete("/{portfolio_id}")
@limiter.limit("1/second")
def delete_portfolio_stock(
    request: Request,
    portfolio_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(authenticate),
):
    stock_portfolio_repository = StockPortfolioRepository(db)
    stock_portfolio_service = StockPortfolioService(stock_portfolio_repository, user_id)
    try:
        stock_portfolio = stock_portfolio_service.delete_portfolio(str(portfolio_id))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "detail": (
            "Usunięto portfel" if stock_portfolio else "Brak portfela do usunięcia"
        )
    }


@router.post("/{portfolio_id}/watched_stocks/{stock_symbol}")
@limiter.limit("5/second")
def add_watched_stock(
    request: Request,
    portfolio_id: UUID,
    stock_symbol: str,
    user_id=Depends(authenticate),
    db: Session = Depends(get_db),
) -> StockPortfolioWatched:
    try:
        stock_repository = StockRepository(db)
        stock_service = StockService(stock_repository)

        stock_portfolio_repository = StockPortfolioRepository(db)
        stock_portfolio_service = StockPortfolioService(
            stock_portfolio_repository, user_id
        )

        stock = stock_service.get_stock_by_symbol(stock_symbol)
        stock_portfolio = stock_portfolio_service.get_portfolio_by_id(
            str(portfolio_id), validate_permission_to_edit=True
        )
        watched_stock = stock_portfolio_service.add_watched_stock_to_portfolio(
            str(portfolio_id), stock
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return watched_stock


@router.delete("/{portfolio_id}/watched_stocks/{stock_symbol}")
@limiter.limit("5/second")
def remove_watched_stock(
    request: Request,
    portfolio_id: UUID,
    stock_symbol: str,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:
        stock_repository = StockRepository(db)
        stock_service = StockService(stock_repository)

        stock_portfolio_repository = StockPortfolioRepository(db)
        stock_portfolio_service = StockPortfolioService(
            stock_portfolio_repository, user_id
        )

        stock = stock_service.get_stock_by_symbol(stock_symbol)

        watched_stock = stock_portfolio_service.delete_watched_stock_from_portfolio(
            str(portfolio_id), stock
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return {"detail": "Usunięto obserwowaną akcję z portfela"}


@router.delete("/{portfolio_id}/watched_stocks")
@limiter.limit("1/second")
def remove_all_watched_stocks(
    request: Request,
    portfolio_id: UUID,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:

        stock_portfolio_repository = StockPortfolioRepository(db)
        stock_portfolio_service = StockPortfolioService(
            stock_portfolio_repository, user_id
        )

        watched_stock = (
            stock_portfolio_service.delete_all_watched_stocks_from_portfolio(
                str(portfolio_id)
            )
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return {"detail": "Usunięto wszystkie obserwowane akcje z portfela"}


@router.get("/{portfolio_id}/transactions")
@limiter.limit("5/second")
def get_portfolio_stock_transactions(
    request: Request,
    portfolio_id: UUID,
    stock_symbol: str = None,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
) -> Page[StockPortfolioTransactions]:
    try:
        if stock_symbol:
            stock_repository = StockRepository(db)
            stock_service = StockService(stock_repository)
            stock = stock_service.get_stock_by_symbol(stock_symbol)
            if stock is None:
                raise NotFoundError(f"Akcja o symbolu {stock_symbol} nie istnieje")

        stock_portfolio_repository = StockPortfolioRepository(db)
        stock_portfolio_service = StockPortfolioService(
            stock_portfolio_repository, user_id
        )

        transactions = stock_portfolio_service.get_transactions_in_portfolio(
            str(portfolio_id), stock=stock if stock_symbol else None
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return paginate(transactions)


@router.post("/{portfolio_id}/transactions")
@limiter.limit("5/second")
def create_portfolio_stock_transaction(
    request: Request,
    portfolio_id: UUID,
    transaction_data: StockPortfolioCreateTransaction,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
) -> StockPortfolioTransactionDetail:

    try:
        stock_repository = StockRepository(db)
        stock_service = StockService(stock_repository)

        transaction_data = transaction_data.model_dump()
        stock = stock_service.get_stock_by_symbol(transaction_data["stock"]["symbol"])
        if stock is None:
            raise NotFoundError(
                f"Akcja o symbolu {transaction_data['stock']['symbol']} nie istnieje"
            )
        stock_portfolio_repository = StockPortfolioRepository(db)
        stock_portfolio_service = StockPortfolioService(
            stock_portfolio_repository, user_id
        )

        transaction_data.update({"portfolio_id": str(portfolio_id), "stock": stock})
        created_transaction = stock_portfolio_service.create_transaction_in_portfolio(
            str(portfolio_id), transaction_data
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return created_transaction


# @router.get("/{portfolio_id}/transactions/{transaction_id}")
# @limiter.limit("5/second")
# def get_detail_portfolio_crypto_transaction(
#     request: Request,
#     portfolio_id: UUID,
#     transaction_id: UUID,
#     user_id: str = Depends(authenticate),
#     db: Session = Depends(get_db),
# ) -> CryptoPortfolioTransactionDetail:
#     try:

#         crypto_portfolio_repository = CryptoPortfolioRepository(db)
#         crypto_portfolio_service = CryptoPortfolioService(
#             crypto_portfolio_repository, user_id
#         )

#         transaction = crypto_portfolio_service.get_transaction_in_portfolio(
#             str(portfolio_id), str(transaction_id)
#         )
#     except BadRequestError as bre:
#         raise HTTPException(status_code=bre.status_code, detail=str(bre))
#     except UnauthorizedError as ue:
#         raise HTTPException(status_code=ue.status_code, detail=str(ue))
#     except NotFoundError as ne:
#         raise HTTPException(status_code=ne.status_code, detail=str(ne))

#     return transaction


@router.patch("/{portfolio_id}/transactions/{transaction_id}")
@limiter.limit("5/second")
def update_portfolio_stock_transaction(
    request: Request,
    portfolio_id: UUID,
    transaction_id: UUID,
    update_transaction_data: StockPortfolioUpdateTransaction,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
) -> StockPortfolioTransactionDetail:

    try:
        stock_repository = StockRepository(db)
        stock_service = StockService(stock_repository)

        stock_portfolio_repository = StockPortfolioRepository(db)
        stock_portfolio_service = StockPortfolioService(
            stock_portfolio_repository, user_id
        )

        update_transaction_data = update_transaction_data.model_dump()
        stock = update_transaction_data.get("stock", None)
        if stock is None:
            pass
        else:
            stock = stock_service.get_stock_by_symbol(
                update_transaction_data["stock"].get("symbol", None)
            )
            if stock is None:
                raise NotFoundError(
                    f"Akcja o symbolu {update_transaction_data['stock']['symbol']} nie istnieje"
                )

        update_transaction_data.update(
            {"stock": stock, "portfolio_id": str(portfolio_id)}
        )
        created_transaction = stock_portfolio_service.update_transaction_in_portfolio(
            str(portfolio_id), str(transaction_id), update_transaction_data
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return created_transaction


@router.delete("/{portfolio_id}/transactions/{transaction_id}")
@limiter.limit("5/second")
def delete_portfolio_stock_transaction(
    request: Request,
    portfolio_id: UUID,
    transaction_id: UUID,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:

        stock_portfolio_repository = StockPortfolioRepository(db)
        stock_portfolio_service = StockPortfolioService(
            stock_portfolio_repository, user_id
        )

        transaction = stock_portfolio_service.delete_transaction_in_portfolio(
            str(portfolio_id), str(transaction_id)
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return {"detail": "Usunięto transakcję z portfela"}


@router.delete("/{portfolio_id}/transactions")
@limiter.limit("5/second")
def delete_portfolio_stock_transactions(
    request: Request,
    portfolio_id: UUID,
    stock_symbol: str = None,
    user_id: str = Depends(authenticate),
    db: Session = Depends(get_db),
):
    try:
        if stock_symbol:
            stock_repository = StockRepository(db)
            stock_service = StockService(stock_repository)
            stock = stock_service.get_stock_by_symbol(stock_symbol)
            if stock is None:
                raise NotFoundError(f"Akcja o symbolu {stock_symbol} nie istnieje")
        stock_portfolio_repository = StockPortfolioRepository(db)
        stock_portfolio_service = StockPortfolioService(
            stock_portfolio_repository, user_id
        )

        transaction = stock_portfolio_service.delete_all_transactions_in_portfolio(
            str(portfolio_id), stock=stock if stock_symbol else None
        )
    except BadRequestError as bre:
        raise HTTPException(status_code=bre.status_code, detail=str(bre))
    except UnauthorizedError as ue:
        raise HTTPException(status_code=ue.status_code, detail=str(ue))
    except NotFoundError as ne:
        raise HTTPException(status_code=ne.status_code, detail=str(ne))

    return {"detail": "Usunięto wszystkie transakcje z portfela"}
