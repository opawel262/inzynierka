from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.domain.user import schemas, services, models
from app.api.deps import get_db

from typing import Union

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", response_model=schemas.UserRetrieve)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return services.create_user(user=user, db=db)
