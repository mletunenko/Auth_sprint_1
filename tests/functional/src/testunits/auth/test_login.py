from src.utils import gen_random_email, gen_random_password


def test_login_user_success(client, create_common_user):
    user_data = create_common_user
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/login", json=user_data)
    assert response.status_code == 200

def test_login_user_wrong_email(client, create_common_user):
    user_data_wrong_email = {
        "email": create_common_user["email"],
        "password": gen_random_password()
    }
    response = client.post("/auth/login", json=user_data_wrong_email)
    assert response.status_code == 401

def test_login_user_wrong_password(client, create_common_user):
    user_data_wrong_password = {
        "email": gen_random_email(),
        "password": create_common_user["password"]
    }
    response = client.post("/auth/login", json=user_data_wrong_password)
    assert response.status_code == 401
