from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta
from pydantic import EmailStr
from fastapi_mail import ConnectionConfig


# General settings
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_ignore_empty=False, env_file="../.env", extra="ignore"
    )
    API_V1_STR: str = "/api/v1"

    JWT_TOKEN_PREFIX: str = "Authorization"

    ALGORITHM: str = "HS256"



    # FROM ENV
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str
    EMAIL_EMAIL: EmailStr
    EMAIL_PASSWORD: str
    
    # AUTH TOKENS EXPIRE TIME 
    ACCESS_TOKEN_EXPIRE_MINUTES: timedelta = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRE_DAYS: timedelta = timedelta(days=10)
    
    # CONFIRMATION ACCOUNT TOKEN EXPIRE TIME
    CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_DAYS: timedelta = timedelta(days=7)
    
    # PASSWORD RESET TOKEN EXPIRE TIME
    PASSWORD_RESET_TOKEN_EXPIRE_TIME_MINUTES: timedelta = timedelta(minutes=15) 

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
