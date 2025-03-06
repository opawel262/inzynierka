from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import authenticate_user, create_token
from . import schemas
from app.domain.user.models import User
from app.domain.auth.schemas import Token
from app.core.config import settings
from datetime import timedelta, datetime, timezone
from typing import Union, Literal, Dict
import jwt


def get_tokens(data: schemas.CreateToken, db: Session) -> Token:

    user = authenticate_user(db=db, email=data.email, password=data.password)

    if not user:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Niepoprawne dane"
        )

    _verify_user_access(user)

    access_token = create_token(
        token_type="access",
        data={"user_id": str(user.id)},
        expire_time=settings.ACCESS_TOKEN_EXPIRE_TIME,
    )

    refresh_token = create_token(
        token_type="refresh",
        data={"user_id": str(user.id)},
        expire_time=settings.REFRESH_TOKEN_EXPIRE_TIME,
    )

    return Token(access_token=access_token, refresh_token=refresh_token)


async def get_access_token_by_refresh_token(refresh_token: str) -> str:

    payload = get_token_payload(refresh_token)

    user_id = payload.get("user_id")

    access_token = create_token(
        token_type="access",
        data={"user_id": str(user_id)},
        expire_time=settings.ACCESS_TOKEN_EXPIRE_TIME,
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

    if not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Twoje konto nie jest potwierdzone",
        )
