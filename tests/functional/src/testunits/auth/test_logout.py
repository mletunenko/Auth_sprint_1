def test_logout_success(client, login_common_user):
    access_token = login_common_user["access"]
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    logout_response = client.post("/auth/logout", headers=headers)
    assert logout_response.status_code == 200
