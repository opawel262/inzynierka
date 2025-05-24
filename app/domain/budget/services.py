from sqlalchemy.orm import Session
from . import schemas, models


async def get_budget_by_id(budget_id: str, user_id: str, db: Session) -> models.Budget:
    return db.query(models.Budget).filter(models.Budget.id == budget_id, models.Budget.owner_id == user_id).first()


async def get_budgets_by_user_id(user_id: str, db: Session) -> list[models.Budget]:
    return db.query(models.Budget).filter(models.Budget.owner_id == user_id).all()


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
