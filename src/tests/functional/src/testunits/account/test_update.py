from http import HTTPStatus

import pytest

from models.user import User


@pytest.mark.asyncio
async def test_auth_update(client, test_user, access_token, test_db_session):
    new_email = "updateduser@mail.com"
    new_password = "newpassword"

    response = await client.patch(
        "/auth/update",
        json={"email": new_email, "password": new_password},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "User information updated successfully"

    # Проверяем обновление данных в БД
    user = await test_db_session.get(User, test_user.id)
    assert user.email == new_email
    assert user.check_password(new_password)


@pytest.mark.asyncio
async def test_auth_update_existing_email(client, test_user, access_token, test_db_session):
    # Создаем другого пользователя с таким же email
    another_user = User(email="existing@mail.com")
    another_user.set_password("testpassword")
    test_db_session.add(another_user)
    await test_db_session.commit()

    response = await client.patch(
        "/auth/update",
        json={"email": another_user.email, "password": "newpassword"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already in use"
