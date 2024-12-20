from http import HTTPStatus
import pytest


@pytest.mark.asyncio(loop_scope='session')
async def test_auth_me(client, test_user, access_token):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email


@pytest.mark.asyncio(loop_scope='session')
async def test_auth_me_unauthorized(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401
