from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
    status,
    UploadFile,
    File,
    Form,
)

from sqlalchemy.orm import Session

from app.domain.user import schemas, services, models
from app.api.deps import get_db, authenticate
from app.core.schemas import EmailSchema, ReponseDetailSchema
from app.core.utils import (
    send_mail,
    validate_email,
    generate_token,
    check_file_if_image,
)
from app.core.responses.user import register_response
from app.core.config import settings
from app.core.security import get_password_hash
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
async def create_user(
    user: schemas.UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    # Email validation
    if not validate_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niepoprawny format adresu email.",
        )

    if services.get_user_by_email(email=user.email, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ten adres email jest już zarejestrowany.",
        )

    if services.get_user_by_username(username=user.username, db=db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nazwa użytkownika jest już zajęta.",
        )

    # Password validation
    if len(user.password) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi mieć co najmniej 12 znaków.",
        )
    if not re.search(r"\d", user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną cyfrę.",
        )
    if not re.search(r"[A-Z]", user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną wielką literę.",
        )
    if not re.search(r"[a-z]", user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną małą literę.",
        )
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':,.<>?/]", user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jeden znak specjalny.",
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
        body={"link": f"{settings.FRONTED_URL}/confirm-user?token={token.value}"},
        subject="Aktywuj konto",
        template_name="email_confirmation",
    )
    background_tasks.add_task(send_mail, email)

    return {"detail": "Proszę sprawdzić swój email, aby aktywować konto."}


@router.post("/confirm/{token}")
async def confirm_user_account(token: str, db: Session = Depends(get_db)):
    token = services.get_token_by_value(token_value=token, db=db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy token sesji.",
        )
    user = services.get_user_by_id(id=token.user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Użytkownik nie istnieje.",
        )
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Konto jest już aktywne.",
        )

    user.is_active = True
    db.commit()
    return {"detail": "Konto zostało pomyślnie aktywowane."}


@router.post("/reset-password")
async def send_reset_password_email(
    body: schemas.Email,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    if not validate_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Niepoprawny format adresu email.",
        )

    user = services.get_user_by_email(email=body.email, db=db)
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
            body={"link": f"{settings.FRONTED_URL}/reset-password?token={token.value}"},
            subject="Resetowanie hasła",
            template_name="password_reset",
        )
        background_tasks.add_task(send_mail, email)

    return {
        "detail": "Jeśli konto z podanym adresem email istnieje, wysłano wiadomość z instrukcjami dotyczącymi zmiany hasła."
    }


@router.post("/reset-password/{token}")
async def reset_user_password(
    token: str, body: schemas.NewPassword, db: Session = Depends(get_db)
):
    token = services.get_token_by_value(token_value=token, db=db)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy token sesji.",
        )

    user = services.get_user_by_id(id=token.user_id, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nieprawidłowy token sesji.",
        )

    if token.expiration_time < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sesja wygasła.",
        )

    # Password validation
    if len(body.new_password) < 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi mieć co najmniej 12 znaków.",
        )
    if not re.search(r"\d", body.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną cyfrę.",
        )
    if not re.search(r"[A-Z]", body.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną wielką literę.",
        )
    if not re.search(r"[a-z]", body.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jedną małą literę.",
        )
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;':,.<>?/]", body.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hasło musi zawierać co najmniej jeden znak specjalny.",
        )

    user.password = get_password_hash(body.new_password)
    db.add(user)
    db.commit()

    services.delete_token_by_value(token_value=token.value, db=db)

    return {"detail": "Hasło zostało pomyślnie zresetowane."}


@router.get("/me")
async def get_user_by_access_token(
    user_id: Annotated[int, Depends(authenticate)],
    db: Session = Depends(get_db),
) -> schemas.UserRetrieve:
    return services.get_user_by_id(id=user_id, db=db)


@router.patch("/me")
async def update_partial_user(
    user_id: Annotated[int, Depends(authenticate)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[Union[schemas.UserUpdate, str], Form(...)] = None,
    avatar_image: Union[Annotated[UploadFile, File(...)]] = None,
) -> schemas.UserRetrieve:

    try:
        if (user or avatar_image) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brak danych do aktualizacji.",
            )
        db_user = services.get_user_by_id(id=user_id, db=db)

        if user:
            user = json.loads(user)
            user_update = schemas.UserUpdate(**user)

        if avatar_image:
            if not check_file_if_image(avatar_image):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Przesłany plik nie jest obrazem.",
                )
            avatar_image.filename = f"{uuid4()}.{avatar_image.filename.split('.')[-1]}"
            print("hel")
            image_content = await avatar_image.read()
            print(avatar_image.filename)
            current_directory = os.getcwd()
            app_directory = os.path.join(current_directory, "app")
            print(f"App directory: {app_directory}")
            print("Files in the app directory:")
            for root, dirs, files in os.walk(app_directory):
                for file_name in files:
                    print(os.path.join(root, file_name))
            print(f"{settings.MEDIA_IMAGE_DIR}/uploads/user/{avatar_image.filename}")
            with open(
                f"{settings.MEDIA_IMAGE_DIR}/uploads/user/{avatar_image.filename}", "wb"
            ) as f:
                f.write(image_content)

            avatar_image_url = (
                f"{settings.MEDIA_IMAGE_URL}/uploads/user/{avatar_image.filename}"
            )

            db_user.avatar_image = avatar_image_url
            print(avatar_image_url)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        print(db_user.avatar_image)
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Błąd serwera: {str(e)}",
        )
