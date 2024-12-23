

def test_register_user_success(client, clear_database):
    user_data = {"email": "test@example.com", "password": "securepassword"}
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200

def test_register_user_already_exists(client, clear_database, create_common_user):
    user_data = create_common_user
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
