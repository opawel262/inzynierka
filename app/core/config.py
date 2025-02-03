from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_ignore_empty=False, env_file="../.env", extra="ignore"
    )
    API_V1_STR: str = "/api/v1"

    JWT_TOKEN_PREFIX: str = "Authorization"

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: timedelta = timedelta(minutes=30)
    REFRESH_TOKEN_EXPIRE_DAYS: timedelta = timedelta(days=10)

    # FROM ENV
    SQLALCHEMY_DATABASE_URL: str
    SECRET_KEY: str


settings = Settings()
