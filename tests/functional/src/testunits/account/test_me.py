from http import HTTPStatus


def test_auth_me(client, login_common_user):
    access_token = login_common_user["access"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == HTTPStatus.OK


def test_auth_me_unauthorized(client, login_common_user):
    access_token = login_common_user["access"]
    headers = {
        "Authorization": f"Bearer {access_token[:-1]}"
    }
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
