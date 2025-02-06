from fastapi import Depends, Request, Cookie, HTTPException, status
from app.domain.auth.services import get_token_payload
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2
from app.core.database import SessionLocal
from app.domain.user.services import get_user_by_id
from sqlalchemy.orm import Session
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        access_token: str = str(
            request.cookies.get("access_token")
        )

        return access_token


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/v1/auth/token")


def get_db():
    """
    Function responsible for giving access to database
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authenticate(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> str:
    """
    Get the current user by using the access token from cookies.

    Parameters:
    - access_token: The access token retrieved from cookies.
    - db: The database session.

    Returns:
    - A dictionary representing the current user.

    Raises:
    - HTTPException: If the access token is invalid or missing.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Nie jesteś zalogowany."
        )
    # Function to retrieve user from token (pseudo-code)
    payload = get_token_payload(access_token)

    user_id = payload.get("user_id")

    user = get_user_by_id(id=user_id, db=db)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Użytkownik jest nieaktywny."
        )

    return user_id
