from http import HTTPStatus

from src.utils import gen_random_email, gen_random_password


def test_auth_update(client, login_common_user):
    new_email = gen_random_email()
    new_password = gen_random_password()
    access_token = login_common_user["access"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    upd_data = {"email": new_email, "password": new_password}
    response = client.patch("/auth/update", headers=headers, json=upd_data)
    assert response.status_code == HTTPStatus.OK


def test_auth_update_valid_error(client, login_common_user, create_extra_user):
    new_email = create_extra_user["email"]
    new_password = gen_random_password()
    access_token = login_common_user["access"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    upd_data = {"email": new_email, "password": new_password}
    response = client.patch("/auth/update", headers=headers, json=upd_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
