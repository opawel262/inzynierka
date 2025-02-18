from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Union, Literal
from datetime import timedelta
from app.domain.user.models import User
from app.domain.user.services import get_user_by_email
from app.domain.auth import schemas
from app.core.config import settings
import jwt
import os
from uuid import uuid4

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str) -> Union[User, False]:
    # authenticate user by checking if user exists by email and if exists check password
    user = get_user_by_email(email=email, db=db)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_token(
    token_type: Literal["access", "refresh"],
    data: dict = None
) -> str:
    """Create jwt token"""
    to_encode = data.copy()

    to_encode.update(
        {
            "token_type": token_type,
        }
    )
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

    return encoded_jwt
