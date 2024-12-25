def test_refresh_token_success(client, login_common_user):
    refresh_token = login_common_user["refresh"]
    headers = {
        "Authorization": f"Bearer {refresh_token}"
    }
    refresh_response = client.post("/auth/refresh", headers=headers)
    assert refresh_response.status_code == 200

def test_refresh_token_invalid(client, login_common_user):
    refresh_token = login_common_user["refresh"]
    headers = {
        "Authorization": f"Bearer {refresh_token[:-1]}"
    }
    refresh_response = client.post("/auth/refresh", headers=headers)
    assert refresh_response.status_code == 401
