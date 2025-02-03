from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import authenticate_user, create_token
from . import schemas
from app.domain.user.models import User
from app.core.config import settings
from datetime import timedelta, datetime, timezone
from typing import Union, Literal
import jwt


async def get_tokens(data: schemas.Token, db: Session) -> dict:
    user = authenticate_user(db=db, email=data.email, password=data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Niepoprawne dane."
        )

    _verify_user_access(user)

    access_token = create_token(
        token_type="access",
        data={"user_id": str(user.id)},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    refresh_token = create_token(
        token_type="refresh",
        data={"user_id": str(user.id)},
        expires_delta=settings.REFRESH_TOKEN_EXPIRE_DAYS,
    )

    return {"access_token": access_token, "refresh_token": refresh_token}


async def get_access_token_by_refresh_token(refresh_token: str) -> str:
    payload = get_token_payload(refresh_token)

    user_id = payload.get("user_id")

    access_token = create_token(
        token_type="access",
        data={"user_id": str(user_id)},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )

    return access_token


def get_token_payload(token: str) -> Union[dict]:
    # decode jwt token to payload
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    return payload


def _verify_user_access(user: User) -> None:
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Twoje konto nie jest potwierdzone.",
        )
