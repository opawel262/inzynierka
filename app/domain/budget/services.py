from sqlalchemy.orm import Session
from . import schemas, models
from typing import Optional, Literal


async def get_budget_by_budget_user_ids(
    budget_id: str, user_id: str, db: Session
) -> models.Budget:
    return (
        db.query(models.Budget)
        .filter(models.Budget.id == budget_id, models.Budget.owner_id == user_id)
        .first()
    )


async def get_budgets_by_user_id(
    user_id: str,
    db: Session,
    sort_order: Literal["asc", "desc"] = "desc",
    sort_by: Literal["created_at", "updated_at"] = "updated_at",
) -> list[models.Budget]:
    query = db.query(models.Budget).filter(models.Budget.owner_id == user_id)

    sort_column = getattr(models.Budget, sort_by)

    if sort_order == "asc":
        sort_column = sort_column.asc()
    else:
        sort_column = sort_column.desc()

    return query.order_by(sort_column).all()


async def create_budget_service(
    budget: schemas.BudgetCreateSchema, user_id: str, db: Session
) -> models.Budget:
    db_budget = models.Budget(**budget.model_dump(), owner_id=user_id)

    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)

    return db_budget


async def update_budget_service(
    budget_id: str, user_id: str, budget_update: schemas.BudgetUpdateSchema, db: Session
) -> models.Budget | None:
    """
    Update a budget if it belongs to the user.
    """
    budget = (
        db.query(models.Budget)
        .filter(models.Budget.id == budget_id, models.Budget.owner_id == user_id)
        .first()
    )

    if not budget:
        return None

    for field, value in budget_update.dict(exclude_unset=True).items():
        setattr(budget, field, value)

    db.commit()
    db.refresh(budget)
    return budget


async def delete_budget_service(budget_id: str, user_id: str, db: Session) -> bool:
    """
    Delete a budget if it belongs to the user.
    """
    budget = (
        db.query(models.Budget)
        .filter(models.Budget.id == budget_id, models.Budget.owner_id == user_id)
        .first()
    )

    if not budget:
        return False

    db.delete(budget)
    db.commit()
    return True


async def get_budget_transactions_service(
    budget_id: str,
    user_id: str,
    db: Session,
    value: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    sort_order: Literal["asc", "desc"] = "desc",
    sort_by: Literal["created_at", "updated_at"] = "created_at",
    by_category_id: Optional[int] = None,
    transaction_type: Optional[str] = None,
) -> list[models.BudgetTransaction]:
    """
    Retrieve filtered and sorted transactions for a specific budget.
    """
    query = db.query(models.BudgetTransaction).filter(
        models.BudgetTransaction.budget_id == budget_id,
        models.BudgetTransaction.budget.has(owner_id=user_id),
    )

    if value:
        query = query.filter(models.BudgetTransaction.title.ilike(f"%{value}%"))

    if min_amount is not None:
        query = query.filter(models.BudgetTransaction.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(models.BudgetTransaction.amount <= max_amount)

    if by_category_id is not None:
        query = query.filter(models.BudgetTransaction.category_id == by_category_id)

    if transaction_type is not None:
        query = query.filter(
            models.BudgetTransaction.transaction_type == transaction_type
        )

    sort_column = getattr(models.BudgetTransaction, sort_by)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = query.order_by(sort_column)

    return query.all()


async def get_budget_transaction_service(
    transaction_id: str, budget_id: str, user_id: str, db: Session
) -> models.BudgetTransaction | None:
    """
    Retrieve a specific budget transaction by its ID.
    """
    return (
        db.query(models.BudgetTransaction)
        .filter(
            models.BudgetTransaction.id == transaction_id,
            models.BudgetTransaction.budget_id == budget_id,
            models.BudgetTransaction.budget.has(owner_id=user_id),
        )
        .first()
    )


async def get_budget_categories_service(db: Session) -> list[models.Category]:
    """
    Retrieve all categories.
    """
    return db.query(models.Category).all()


async def create_budget_transaction_service(
    budget_transaction: schemas.BudgetTransactionCreateSchema,
    budget_id: str,
    user_id: str,
    db: Session,
) -> models.BudgetTransaction:
    """
    Create a new budget transaction.
    """
    db_transaction = models.BudgetTransaction(
        **budget_transaction.model_dump(), budget_id=budget_id
    )

    budget = await get_budget_by_budget_user_ids(budget_id, user_id, db)

    if not budget:
        return None

    if str(budget.owner_id) != str(user_id):
        return None

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


async def update_budget_transaction_service(
    transaction_id: str,
    budget_id: str,
    user_id: str,
    budget_transaction_update: schemas.BudgetTransactionUpdateSchema,
    db: Session,
) -> models.BudgetTransaction | None:
    """
    Update a budget transaction if it belongs to the user.
    """
    transaction = (
        db.query(models.BudgetTransaction)
        .filter(
            models.BudgetTransaction.budget_id == budget_id,
            models.BudgetTransaction.id == transaction_id,
            models.BudgetTransaction.budget.has(owner_id=user_id),
        )
        .first()
    )

    if not transaction:
        return None

    for field, value in budget_transaction_update.dict(exclude_unset=True).items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


async def delete_budget_transaction_service(
    transaction_id: str, budget_id: str, user_id: str, db: Session
) -> bool:
    """
    Delete a budget transaction if it belongs to the user.
    """
    transaction = (
        db.query(models.BudgetTransaction)
        .filter(
            models.BudgetTransaction.budget_id == budget_id,
            models.BudgetTransaction.id == transaction_id,
            models.BudgetTransaction.budget.has(owner_id=user_id),
        )
        .first()
    )

    if not transaction:
        return False

    db.delete(transaction)
    db.commit()
    return True
