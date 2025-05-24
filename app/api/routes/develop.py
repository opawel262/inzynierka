from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy import MetaData, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.domain.model_base import Base
from app.core.database import engine
from app.api.deps import get_db
from app.core.utils import limiter
from app.core.security import get_password_hash
from app.core.config import settings
from app.domain.user.models import User
from app.domain.budget.models import Category
from app.domain.budget.utils import categories
router = APIRouter(
    prefix="/develop",
    tags=["Development Utilities"],
)


@router.delete("/clear-database")
@limiter.limit("60/minute")
def clear_data(request: Request, db: Session = Depends(get_db)):
    try:
        metadata = MetaData()
        metadata.reflect(bind=engine)

        with engine.connect() as conn:
            # Disable foreign key checks if necessary (depends on your DBMS)
            # conn.execute("SET FOREIGN_KEY_CHECKS = 0")

            # Delete all rows from tables in reverse order to handle foreign key constraints
            for table in reversed(metadata.sorted_tables):
                conn.execute(table.delete())

            # Commit the transaction
            conn.commit()

            # Enable foreign key checks if you disabled them
            # conn.execute("SET FOREIGN_KEY_CHECKS = 1")

        return {"message": "All data cleared successfully"}

    except SQLAlchemyError as e:
        db.rollback()  # Ensure the session is rolled back on error
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/drop-database-tables")
@limiter.limit("60/minute")
def drop_all_tables(request: Request, db: Session = Depends(get_db)):
    try:
        # Reflect the metadata from the database
        metadata = MetaData()
        metadata.reflect(bind=engine)

        with engine.connect() as conn:
            # Begin a transaction
            with conn.begin():
                # Drop tables in reverse order
                for table in reversed(metadata.sorted_tables):
                    drop_table_sql = f"DROP TABLE IF EXISTS {table.name} CASCADE"
                    conn.execute(text(drop_table_sql))

        return {"message": "All tables dropped successfully"}

    except SQLAlchemyError as e:
        db.rollback()  # Roll back the transaction in case of error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR500, detail=str(e)
        )

@router.post("/create-example-data")
def create_example_data(request: Request, db: Session = Depends(get_db)):
    if db.query(User).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Example data already exists. Clear the database first.",
        )
    user1 = User(
        email=settings.EXAMPLE_USER_EMAIL,
        username=settings.EXAMPLE_USER_USERNAME,
        password=get_password_hash(settings.EXAMPLE_USER_PASSWORD),
        is_active=True,
    )
    user2 = User(
        email=settings.EXAMPLE_USER_2_EMAIL,
        username=settings.EXAMPLE_USER_2_USERNAME,
        password=get_password_hash(settings.EXAMPLE_USER_2_PASSWORD),
        is_active=True,
    )
    db.add(user1)
    db.add(user2)
    
    for category in categories:
        category = Category(
            name=category.get("name"),
            icon=category.get("icon"),
        )
        db.add(category)
        
    db.commit()
    
    return {"message": "Example data created successfully"}

