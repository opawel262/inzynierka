from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi_pagination import Page, paginate

from sqlalchemy.orm import Session
from app.api.deps import get_db, authenticate
from app.core.utils import limiter
from app.domain.budget.schemas import (
    BudgetCreateSchema,
    BudgetSchema,
    BudgetUpdateSchema,
    BudgetTransactionCreateSchema,
    BudgetTransactionUpdateSchema,
    BudgetTransactionDetailSchema,
    BudgetTransactionCategoryDetailSchema,
)
from app.domain.budget.models import Budget
from app.domain.budget.services import (
    get_budget_by_id,
    create_budget_service,
    update_budget_service,
    delete_budget_service,
    get_budget_transactions_service,
    create_budget_transaction_service,
    update_budget_transaction_service,
    get_budget_categories_service,
    get_budget_transaction_service,
    delete_budget_transaction_service,
)
from typing import Annotated

router = APIRouter(
    prefix="/budgets",
    tags=["Budget Management"],
)


@router.get("/categories")
async def get_budget_transaction_categories(
    request: Request,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> Page[BudgetTransactionCategoryDetailSchema]:
    """
    Get all budget transaction categories.
    """
    categories = await get_budget_categories_service(db=db)

    if not categories:
        raise HTTPException(status_code=404, detail="Nie znaleziono kategorii budżetu")

    return paginate(categories)


@router.get("")
@limiter.limit("50/minute")
async def get_all_budgets(
    request: Request, db: Session = Depends(get_db), user_id=Depends(authenticate)
) -> Page[BudgetSchema]:
    """
    Retrieve all budgets for the authenticated user.
    """
    budgets = db.query(Budget).filter(Budget.owner_id == user_id).all()
    return paginate(budgets)


@router.post("")
@limiter.limit("10/minute")
async def create_budget(
    request: Request,
    budget: BudgetCreateSchema,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> BudgetSchema:
    """
    Create a new budget for the authenticated user.
    """
    budget = await create_budget_service(budget=budget, user_id=user_id, db=db)

    return budget


@router.get("/{budget_id}")
@limiter.limit("30/minute")
async def get_budget(
    request: Request,
    budget_id: str,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> BudgetSchema:
    """
    Get a single budget by ID.
    """
    budget = await get_budget_by_id(budget_id=budget_id, user_id=user_id, db=db)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.patch("/{budget_id}")
@limiter.limit("50/minute")
async def update_budget(
    request: Request,
    budget_id: str,
    budget_update: BudgetUpdateSchema,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> BudgetSchema:
    """
    Update a budget.
    """
    updated_budget = await update_budget_service(
        budget_id=budget_id, user_id=user_id, budget_update=budget_update, db=db
    )
    if not updated_budget:
        raise HTTPException(
            status_code=404, detail="Budżet nie znaleziony lub brak dostępu"
        )
    return updated_budget


@router.delete("/{budget_id}", status_code=204)
@limiter.limit("5/minute")
async def delete_budget(
    request: Request,
    budget_id: str,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
):
    """
    Delete a budget.
    """
    success = await delete_budget_service(budget_id=budget_id, user_id=user_id, db=db)
    if not success:
        raise HTTPException(
            status_code=404, detail="Budżet nie znaleziony lub brak dostępu"
        )


@router.get("/budgets/{budget_id}/transactions")
async def get_budget_transactions(
    request: Request,
    budget_id: str,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> Page[BudgetTransactionDetailSchema]:
    """
    Get all transactions for a specific budget.
    """
    transactions = await get_budget_transactions_service(
        budget_id=budget_id, user_id=user_id, db=db
    )
    return paginate(transactions)


@router.get("/budgets/{budget_id}/transactions/{transaction_id}")
async def get_budget_transaction(
    request: Request,
    budget_id: str,
    transaction_id: str,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> BudgetTransactionDetailSchema:
    """
    Get a specific transaction for a budget.
    """
    transaction = await get_budget_transaction_service(
        transaction_id=transaction_id, budget_id=budget_id, user_id=user_id, db=db
    )

    if not transaction:
        raise HTTPException(
            status_code=404, detail="Transakcja nie znaleziona lub brak dostępu"
        )

    return transaction


@router.post("/budgets/{budget_id}/transactions")
async def create_budget_transaction(
    request: Request,
    budget_transaction: BudgetTransactionCreateSchema,
    budget_id: str,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> BudgetTransactionDetailSchema:
    """
    Create a new transaction for a specific budget.
    """
    transaction = await create_budget_transaction_service(
        budget_transaction=budget_transaction,
        budget_id=budget_id,
        user_id=user_id,
        db=db,
    )
    return transaction


@router.patch("/budgets/{budget_id}/transactions/{transaction_id}")
async def update_budget_transaction(
    request: Request,
    budget_id: str,
    transaction_id: str,
    budget_transaction_update: BudgetTransactionUpdateSchema,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> BudgetTransactionDetailSchema:
    """
    Update a specific budget transaction.
    """
    updated_transaction = await update_budget_transaction_service(
        budget_id=budget_id,
        transaction_id=transaction_id,
        user_id=user_id,
        budget_transaction_update=budget_transaction_update,
        db=db,
    )

    if not updated_transaction:
        raise HTTPException(
            status_code=404, detail="Transakcja nie znaleziona lub brak dostępu"
        )

    return updated_transaction


@router.delete("/budgets/{budget_id}/transactions/{transaction_id}", status_code=204)
async def delete_budget_transaction(
    request: Request,
    budget_id: str,
    transaction_id: str,
    user_id: Annotated[str, Depends(authenticate)],
    db: Session = Depends(get_db),
):
    """
    Delete a specific budget transaction.
    """
    success = await delete_budget_transaction_service(
        budget_id=budget_id, transaction_id=transaction_id, user_id=user_id, db=db
    )

    if not success:
        raise HTTPException(
            status_code=404, detail="Transakcja nie znaleziona lub brak dostępu"
        )
