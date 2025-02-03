from fastapi import Depends, Request, Cookie, HTTPException, status
from app.domain.auth.services import get_token_payload
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordBearer
from app.core.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token-openai-cookie")


def get_db():
    """
    Function responsible for giving access to database
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    access_token: Optional[str] = Cookie(None),
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

    return user_id
