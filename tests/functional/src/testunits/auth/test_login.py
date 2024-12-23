def test_login_user_success(client, clear_database, create_common_user):
    user_data = create_common_user
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/login", json=user_data)
    assert response.status_code == 200

def test_login_user_wrong_email(client, clear_database, create_common_user):
    user_data_wrong_email = {"email": "wrong@example.com", "password": "securepassword"}
    response = client.post("/auth/login", json=user_data_wrong_email)
    assert response.status_code == 401

def test_login_user_wrong_password(client, clear_database, create_common_user):
    user_data_wrong_email = {"email": "test@example.com", "password": "wrong"}
    response = client.post("/auth/login", json=user_data_wrong_email)
    assert response.status_code == 401

