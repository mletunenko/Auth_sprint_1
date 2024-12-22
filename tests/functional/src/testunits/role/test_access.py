from http import HTTPStatus

import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_token_required_to_access_views(
    role_endpoints, normal_user, make_post_request, make_get_request
):
    for endpoint, method in role_endpoints.items():
        if method == "get":
            body, status = await make_get_request(endpoint)
        elif method == "post":
            body, status = await make_post_request(endpoint)
        assert status == HTTPStatus.UNAUTHORIZED

    body, status = await make_post_request(
        "/login", data={"email": normal_user.email, "password": "hashedpassword123"}
    )

    headers = {"Authorization": f"Bearer {body["access"]}"}

    for endpoint, method in role_endpoints.items():
        if method == "get":
            body, status = await make_get_request(endpoint, headers=headers)
        elif method == "post":
            body, status = await make_post_request(endpoint, headers=headers)
        assert status != HTTPStatus.UNAUTHORIZED
