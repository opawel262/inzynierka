from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response, Request

from sqlalchemy.orm import Session

from app.domain.auth.schemas import Token, CreateToken, AccessToken

from app.domain.auth.services import get_tokens, get_access_token_by_refresh_token
from app.domain.auth.schemas import Token

from app.core.config import settings
from app.core.schemas import ResponseDetailSchema
from app.core.utils import limiter
from app.api.deps import get_db

from typing import Union, Optional, Annotated, Dict

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/token", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/second")
async def authenticate_user(
    request: Request,
    response: Response,
    data: CreateToken,
    db: Session = Depends(get_db),
) -> ResponseDetailSchema:

    tokens = get_tokens(data=data, db=db)

    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        max_age=int((settings.ACCESS_TOKEN_EXPIRE_TIME.total_seconds())),
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        max_age=int(settings.REFRESH_TOKEN_EXPIRE_TIME.total_seconds()),
    )

    return {"detail": "Uwierzytelnienie zakończone pomyślnie"}


@router.post(
    "/refresh-token",
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("1/second")
async def refresh_token(
    request: Request, response: Response, refresh_token: Optional[str] = Cookie(None)
) -> ResponseDetailSchema:

    access_token = await get_access_token_by_refresh_token(refresh_token)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=int(settings.ACCESS_TOKEN_EXPIRE_TIME.total_seconds()),
    )

    return {"detail": "Token odświeżony pomyślnie"}


@router.delete("/logout", status_code=status.HTTP_200_OK)
@limiter.limit("1/second")
async def logout(request: Request, response: Response) -> ResponseDetailSchema:

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return {"detail": "Wylogowano"}
