from app.tests.conftest import authorized_client
from app.core.utils import send_mail
from app.domain.user.services import get_user_by_email
from fastapi.testclient import TestClient
from fastapi import status
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
import os
import time
import pytest
from unittest.mock import AsyncMock
from pytest_mock import mocker, MockerFixture


# Mock class to simulate email response
class MockEmail:
    def __init__(self, token):
        self.body = {"token": token}


@pytest.mark.asyncio
async def test_user_register_and_confirm(
    mocker: MockerFixture, client: TestClient, session: Session
):
    # Mock send_mail and background task
    mock_send_mail = mocker.patch("app.core.utils.send_mail", new_callable=AsyncMock)
    mock_background_task = mocker.patch.object(
        BackgroundTasks, "add_task", new_callable=AsyncMock
    )

    register_data = {
        "email": "test@test.pl",
        "password": "Password123!",
        "firstname": "First",
        "lastname": "Last",
    }

    res = client.post("/users/register", json=register_data)

    assert res.status_code == 201
    assert res.json() == {"detail": "Proszę sprawdzić swój email, aby aktywować konto."}

    assert mock_background_task.call_count == 1

    mock_send_mail.assert_not_called()

    background_task_args = mock_background_task.call_args[0]
    assert background_task_args[0] == send_mail

    email_args = background_task_args[1]

    token = email_args.body["token"]
    confirm_res = client.post(f"/users/confirm/{token}")

    assert confirm_res.status_code == 200
    assert confirm_res.json() == {"detail": "Konto zostało pomyślnie aktywowane."}

    user = get_user_by_email("test@test.pl", session)
    assert user.is_active is True
