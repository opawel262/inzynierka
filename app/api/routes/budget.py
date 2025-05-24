from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi_pagination import Page, paginate

from sqlalchemy.orm import Session
from app.api.deps import get_db, authenticate
from app.core.utils import limiter
from app.domain.budget.schemas import (
    BudgetCreateSchema,
    BudgetSchema,
    BudgetUpdateSchema,
)
from app.domain.budget.models import Budget
from app.domain.budget.services import (
    get_budget_by_id,
    create_budget_service,
    update_budget_service,
    delete_budget_service,
)
from typing import Annotated

router = APIRouter(
    prefix="/budgets",
    tags=["Budget Management"],
)


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
