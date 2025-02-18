from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import server_app
from app.domain.model_base import Base
from app.domain.user.models import User
from app.core.config import settings
from app.core.security import get_password_hash
from app.domain.auth.services import get_tokens
from app.domain.auth.schemas import CreateToken
from app.api.deps import get_db
from typing import Generator, Dict
from time import sleep
import pytest
import json
import datetime
import jwt

connection_engine = None

while connection_engine is None:
    try:
        connection_engine = create_engine(
            settings.SQLALCHEMY_DATABASE_URL, connect_args={}
        )
    except Exception as e:
        print(f"Error occurred when trying to connect to database:\n\n{e}")
        print(f"Retrying in 3s...")
        sleep(3)

engine = connection_engine

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session() -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    with TestClient(server_app) as c:
        # base url
        c.base_url = f"{settings.BACKEND_URL}/api/v1"

        def override_get_db():
            try:
                yield session
            finally:
                session.close()

        server_app.dependency_overrides[get_db] = override_get_db

        yield c


@pytest.fixture
def create_user(db: Session) -> dict:
    user_data = {
        "email": "adam@adam.pl",
        "password": get_password_hash("PasswordExample"),
        "first_name": "adam",
        "last_name": "adam",
        "is_active": True,
    }
    user = User(**user_data)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


@pytest.fixture
def create_tokens(create_user: User, db: Session):
    return
    get_tokens(
        CreateToken(email=create_user.email, password=create_user.passsword), db=session
    )


@pytest.fixture
def authorized_client(client: TestClient, create_tokens: Dict) -> TestClient:
    client.cookies.set("access_token", create_tokens.access_token)
    client.cookies.set("refresh_token", create_tokens.refresh_token)

    return client
