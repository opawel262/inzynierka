from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
from sqlalchemy.orm import Session
from app.domain.auth.schemas import Token, CreateToken, AccessToken
from app.domain.auth.services import get_tokens, get_access_token_by_refresh_token
from app.domain.auth.schemas import Token
from app.core.config import settings
from app.api.deps import get_db
from typing import Union, Optional, Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/token-cookie", response_model=Token, status_code=status.HTTP_201_CREATED)
async def authenticate_user(
    response: Response, data: CreateToken, db: Session = Depends(get_db)
) -> Token:
    tokens = await get_tokens(data=data, db=db)

    response.set_cookie(
        key="access_token",
        value=tokens.get("access_token"),
        httponly=True,
        max_age=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES.total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.get("refresh_token"),
        httponly=True,
        max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS.total_seconds()),
    )

    return Token(**tokens)


@router.post(
    "/token-openai-cookie", response_model=Token, status_code=status.HTTP_201_CREATED
)
async def authenticate_user_form(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    if form_data:
        data = CreateToken(email=form_data.username, password=form_data.password)

    tokens = await get_tokens(data=data, db=db)

    response.set_cookie(
        key="access_token",
        value=tokens.get("access_token"),
        httponly=True,
        max_age=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES.total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.get("refresh_token"),
        httponly=True,
        max_age=int(settings.REFRESH_TOKEN_EXPIRE_DAYS.total_seconds()),
    )

    return Token(**tokens)


@router.post(
    "/refresh-token-cookie",
    response_model=AccessToken,
    status_code=status.HTTP_201_CREATED,
)
async def refresh_token(
    response: Response, refresh_token: Optional[str] = Cookie(None)
):
    access_token = await get_access_token_by_refresh_token(refresh_token)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES.total_seconds()),
    )

    return {"access_token": access_token}
