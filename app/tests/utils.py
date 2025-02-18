from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.domain.article.models import Article, ArticleComment, WishList, Collection
from app.domain.support.models import Issue
from app.domain.user.models import User, Skill, SkillList, Follower
from app.domain.user.service import hash_password
import os
import json
import random
import faker
from typing import List, Final
import pytest

DEFAULT_IMAGE_PATH: Final[str] = os.path.join(
    os.getcwd(), "app", "media", "uploads", "user", "default_article_title_img.jpg"
)


def create_test_user(session: Session) -> User:
    email_test = "test@test.pl"
    count = 0

    while True:
        if not session.query(User).filter_by(email=email_test).first():
            break

        count += 1
        email_test = f"test@test{count}.pl"

    user_data = {
        "email": email_test,
        "password": hash_password("PasswordExample"),
        "username": "username",
        "is_active": True,
    }

    user = User(**user_data)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user


def create_test_unactive_user(session: Session) -> User:
    user_data = {
        "email": "test@test.pl",
        "hashed_password": hash_password("PasswordExample"),
        "username": "username",
        "is_active": False,
    }

    user = User(**user_data)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
