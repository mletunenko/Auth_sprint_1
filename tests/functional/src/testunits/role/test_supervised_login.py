from http import HTTPStatus

import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_token_required_to_access_view(make_post_request, normal_user):
    _, status = await make_post_request(f"/supervised_login/{normal_user.id}")
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_superuser_required_in_token_claims(
    normal_user, access_token_normal_user, make_post_request
):
    headers = {"Authorization": f"Bearer {access_token_normal_user}"}
    body, status = await make_post_request(
        f"/supervised_login/{normal_user.id}", headers=headers
    )
    assert status == HTTPStatus.FORBIDDEN
    assert body["detail"] == "Access forbidden: Superuser required"


@pytest.mark.asyncio(loop_scope="session")
async def test_resuest_logs_in_user(make_post_request, normal_user, access_token_super_user):
    headers = {"Authorization": f"Bearer {access_token_super_user}"}
    body, status = await make_post_request(
        f"/supervised_login/{normal_user.id}", headers=headers
    )
    assert status == HTTPStatus.OK
    assert "access" in body and "refresh" in body
