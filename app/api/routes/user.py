from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
    status,
    UploadFile,
    File,
    Form,
    Request,
)

from sqlalchemy.orm import Session

from app.domain.user import schemas, services, models
from app.api.deps import get_db, authenticate
from app.core.schemas import EmailSchema, ResponseDetailSchema
from app.core.utils import (
    send_mail,
    validate_email,
    generate_token,
    check_file_if_image,
    limiter,
)
from app.core.responses.user import register_response
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.core.database import redis_db
from datetime import timedelta, datetime
from typing import Union, Annotated
import re
import json
from uuid import uuid4
import os

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "/register", responses=register_response, status_code=status.HTTP_201_CREATED
)
@limiter.limit("10/minute")
async def create_user(
    request: Request,
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
) -> ResponseDetailSchema:
    # Email validation
    if not validate_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niepoprawny format adresu email",
        )

    if services.get_user_by_email(email=user.email, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ten adres email jest już zarejestrowany",
        )

    if services.get_user_by_username(username=user.username, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nazwa użytkownika jest już zajęta",
        )

    # Password validation
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi mieć co najmniej 8 znaków",
        )
    if not re.search(r"\d", user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną cyfrę",
        )
    if not re.search(r"[A-Z]", user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną wielką literę",
        )
    if not re.search(r"[a-z]", user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną małą literę",
        )
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':,.<>?/]", user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jeden znak specjalny",
        )

    user = services.create_user(user=user, db=db)
    token = services.create_user_token(
        user_id=user.id,
        token_value=generate_token(length=32),
        token_for="confirmation",
        expiration_time=settings.CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_DAYS,
        db=db,
    )
    email = EmailSchema(
        email=[user.email],
        body={"link": f"{settings.FRONTED_URL}/auth/confirm-user?token={token.value}"},
        subject="Aktywuj konto",
        template_name="email_confirmation",
    )
    background_tasks.add_task(send_mail, email)

    return {"detail": "Proszę sprawdzić swój email, aby aktywować konto"}


@router.post("/confirm/{token}")
@limiter.limit("10/minute")
async def confirm_user_account(
    request: Request, token: str, db: Annotated[Session, Depends(get_db)]
) -> ResponseDetailSchema:
    token = services.get_token_by_value(token_value=token, db=db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy token sesji",
        )
    user = services.get_user_by_id(id=token.user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Użytkownik nie istnieje",
        )
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Konto jest już aktywne",
        )

    user.is_active = True
    db.commit()
    return {"detail": "Konto zostało pomyślnie aktywowane"}


@router.post("/reset-password")
@limiter.limit("50/minute")
async def send_reset_password_email(
    request: Request,
    body: schemas.Email,
    background_tasks: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
) -> ResponseDetailSchema:
    if not validate_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niepoprawny format adresu email",
        )

    user = services.get_user_by_email(email=body.email, db=db)

    email_redis_key = f"reset_password_email:{user.email}"
    attempts = redis_db.get(email_redis_key)

    if attempts and int(attempts) >= settings.RESET_LIMIT_EMAIL_RESET_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Osiągnięto limit prób resetowania hasła. Spróbuj ponownie za 30 minut",
        )

    if user is not None:
        token = services.create_user_token(
            user_id=user.id,
            token_value=generate_token(length=32),
            token_for="confirmation",
            expiration_time=settings.PASSWORD_RESET_TOKEN_EXPIRE_TIME_MINUTES,
            db=db,
        )

        email = EmailSchema(
            email=[user.email],
            body={
                "link": f"{settings.FRONTED_URL}/auth/reset-password?token={token.value}"
            },
            subject="Resetowanie hasła",
            template_name="password_reset",
        )
        background_tasks.add_task(send_mail, email)

        if attempts:
            redis_db.incr(email_redis_key)
        else:
            redis_db.setex(
                email_redis_key, settings.RESET_TIMEOUT_EMAIL_RESET_PASSWORD_IN_SEC, 1
            )

    return {
        "detail": "Jeśli konto z podanym adresem email istnieje, wysłano wiadomość z instrukcjami dotyczącymi zmiany hasła."
    }


@router.post("/reset-password/{token}")
@limiter.limit("50/minute")
async def reset_user_password(
    request: Request,
    token: str,
    body: schemas.NewPassword,
    db: Annotated[Session, Depends(get_db)],
) -> ResponseDetailSchema:
    token = services.get_token_by_value(token_value=token, db=db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy token sesji",
        )

    user = services.get_user_by_id(id=token.user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nieprawidłowy token sesji",
        )

    if token.expiration_time < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sesja wygasła",
        )

    # Password validation
    if len(body.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi mieć co najmniej 8 znaków",
        )
    if not re.search(r"\d", body.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną cyfrę",
        )
    if not re.search(r"[A-Z]", body.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną wielką literę",
        )
    if not re.search(r"[a-z]", body.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną małą literę",
        )
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':,.<>?/]", body.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jeden znak specjalny",
        )

    user.password = get_password_hash(body.new_password)
    db.add(user)
    db.commit()

    services.delete_token_by_value(token_value=token.value, db=db)

    return {"detail": "Hasło zostało pomyślnie zresetowane"}


@router.get("/me")
@limiter.limit("10/minute")
async def get_user_by_access_token(
    request: Request,
    user_id: Annotated[str, Depends(authenticate)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.UserRetrieve:
    return services.get_user_by_id(id=user_id, db=db)


@router.patch("/me")
@limiter.limit("60/minute")
async def update_partial_user_by_access_token(
    request: Request,
    user_id: Annotated[str, Depends(authenticate)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Union[schemas.UserUpdate, str], Form(...)] = None,
    avatar_image: Union[Annotated[UploadFile, File(...)]] = None,
) -> schemas.UserRetrieve:

    try:
        if (user or avatar_image) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brak danych do aktualizacji",
            )

        db_user = services.get_user_by_id(id=user_id, db=db)

        if user:
            user = json.loads(user)
            if services.get_user_by_username(user["username"], db):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Podana nazwa użytkownika jest zajęta",
                )
            db_user.username = user["username"]

        if avatar_image:
            if not check_file_if_image(avatar_image):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Przesłany plik nie jest obrazem",
                )

            avatar_image.filename = f"{uuid4()}.{avatar_image.filename.split('.')[-1]}"
            image_content = await avatar_image.read()

            with open(
                f"{settings.MEDIA_IMAGE_DIR}/uploads/user/{avatar_image.filename}", "wb"
            ) as f:
                f.write(image_content)

            avatar_image_url = (
                f"{settings.MEDIA_IMAGE_URL}/uploads/user/{avatar_image.filename}"
            )

            db_user.avatar_image = avatar_image_url

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

        return db_user

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd serwera: {str(e)}",
        )


@router.delete("/me")
@limiter.limit("50/minute")
async def delete_user_by_access_token(
    request: Request,
    password_user: schemas.PasswordUser,
    user_id: Annotated[str, Depends(authenticate)],
    db: Annotated[Session, Depends(get_db)],
) -> ResponseDetailSchema:
    user = services.get_user_by_id(user_id, db)
    if not verify_password(password_user.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowe hasło",
        )

    db.delete(user)
    db.commit()

    return {"detail": "Konto zostało pomyślnie usunięte"}


@router.put("/me/avatar-image/reset-default")
@limiter.limit("50/minute")
async def reset_user_avatar_to_default(
    request: Request,
    user_id: Annotated[str, Depends(authenticate)],
    db: Annotated[Session, Depends(get_db)],
) -> schemas.AvatarImageUser:
    db_user = services.get_user_by_id(user_id, db)

    if db_user.avatar_image == settings.DEFAULT_USER_AVATAR_IMAGE_URL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Avatar użytkownika jest już ustawiony na domyślny",
        )

    db_user.avatar_image = settings.DEFAULT_USER_AVATAR_IMAGE_URL
    db.commit()
    db.refresh(db_user)

    return db_user


@router.post("/me/reset-password")
@limiter.limit("50/minute")
async def reset_password_user_by_access_token(
    request: Request,
    reset_password: schemas.ResetPasswordUser,
    user_id: Annotated[str, Depends(authenticate)],
    db: Annotated[Session, Depends(get_db)],
) -> ResponseDetailSchema:
    db_user = services.get_user_by_id(user_id, db)
    print(get_password_hash(reset_password.password))
    print(db_user.password)
    if not verify_password(reset_password.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowe hasło",
        )
    db_user.password = get_password_hash(reset_password.new_password)
    print(db_user.password)
    db.refresh(db_user)
    db.commit()

    return {"detail": "Hasło zostało pomyślnie zmienione"}
