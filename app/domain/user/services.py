from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models
from typing import Union, Literal
from datetime import timedelta, datetime


def create_user(user: schemas.UserCreate, db: Session) -> models.User:
    from app.core.security import get_password_hash

    user.password = get_password_hash(user.password)

    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_email(email: str, db: Session) -> models.User:
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(username: str, db: Session) -> models.User:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(id: str, db: Session) -> models.User:
    return db.query(models.User).filter(models.User.id == id).first()


def create_user_token(
    user_id: int,
    token_value: str,
    token_for: Literal["confirmation", "password_reset"],
    expiration_time: timedelta,
    db: Session,
) -> models.Token:
    db_token = models.Token(
        user_id=user_id,
        value=token_value,
        token_for=token_for,
        expiration_time=datetime.utcnow() + expiration_time,
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token


def get_token_by_value(token_value: str, db: Session) -> models.Token:
    return db.query(models.Token).filter(models.Token.value == token_value).first()


def delete_token_by_value(token_value: str, db: Session) -> None:
    token = db.query(models.Token).filter(models.Token.value == token_value).first()

    if token:
        db.delete(token)
        db.commit()
