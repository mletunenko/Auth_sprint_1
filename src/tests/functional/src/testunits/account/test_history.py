from http import HTTPStatus
import pytest
from models.history import LoginHistory


@pytest.mark.asyncio
async def test_auth_history(client, test_user, access_token, test_db_session):
    # Добавляем историю входов
    history = LoginHistory(
        user_id=test_user.id,
        ip_address="127.0.0.1",
        user_agent="test-agent"
    )
    test_db_session.add(history)
    await test_db_session.commit()

    # Запрос истории
    response = await client.get(
        "/auth/history",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["ip_address"] == "127.0.0.1"
    assert response.json()[0]["user-agent"] == "test-agent"


@pytest.mark.asyncio
async def test_auth_history_unauthorized(client):
    response = await client.get("/auth/history")
    assert response.status_code == 401
