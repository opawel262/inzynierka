from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta
from pydantic import EmailStr, validator
from fastapi_mail import ConnectionConfig
from app.gpw_tickers import GPW_TICKERS
from typing import List


# General settings
class Settings(BaseSettings):
    # Use ConfigDict directly without using model_config
    class Config:
        env_file = "../.env"
        env_ignore_empty = False
        extra = "ignore"

    API_V1_STR: str = "/api/v1"

    JWT_TOKEN_PREFIX: str = "Authorization"

    ALGORITHM: str = "HS256"

    GPW_TICKERS: List[str] = GPW_TICKERS
    COINGECKO_API_KEY: str

    # Rate limiter for email
    RESET_LIMIT_EMAIL_RESET_PASSWORD: int = 3
    RESET_TIMEOUT_EMAIL_RESET_PASSWORD_IN_SEC: int = 1800  # 30 minutes
    # AUTH TOKENS EXPIRE TIME
    ACCESS_TOKEN_EXPIRE_TIME: timedelta = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRE_TIME: timedelta = timedelta(days=10)

    # CONFIRMATION ACCOUNT TOKEN EXPIRE TIME
    CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_DAYS: timedelta = timedelta(days=7)

    # PASSWORD RESET TOKEN EXPIRE TIME
    PASSWORD_RESET_TOKEN_EXPIRE_TIME_MINUTES: timedelta = timedelta(minutes=15)

    # static media
    DEFAULT_USER_AVATAR_IMAGE_URL: str = "/static/defaults/user_avatar.png"
    MEDIA_IMAGE_URL: str = "/media"
    MEDIA_IMAGE_DIR: str = "/code/app/media"

    # FROM ENV
    FRONTED_URL: str
    BACKEND_URL: str

    SQLALCHEMY_DATABASE_URL: str

    REDIS_HOST: str
    REDIS_PORT: str

    SECRET_KEY: str

    EMAIL_EMAIL: EmailStr
    EMAIL_PASSWORD: str

    # example user data 1
    EXAMPLE_USER_EMAIL: str
    EXAMPLE_USER_USERNAME: str
    EXAMPLE_USER_PASSWORD: str
    # example user data 2
    EXAMPLE_USER_2_EMAIL: str
    EXAMPLE_USER_2_USERNAME: str
    EXAMPLE_USER_2_PASSWORD: str


settings = Settings()

# EMAIL CONFIGURATION
email_conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_EMAIL,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_EMAIL,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_FROM_NAME="AssetFlow",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="app/templates/email",
    MAIL_PORT=587,
    VALIDATE_CERTS=True,
)
