from src.utils import gen_random_email, gen_random_password


def test_register_user_success(client):
    user_data = {"email": gen_random_email(),
                 "password": gen_random_password()}
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200

def test_register_user_already_exists(client, create_common_user):
    user_data = create_common_user
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
