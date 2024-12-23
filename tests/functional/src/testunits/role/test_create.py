from http import HTTPStatus

import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_token_required_to_access_view(make_post_request):
    _, status = await make_post_request("/role/create")
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_superuser_required_in_token_claims(access_token_normal_user, make_post_request):
    headers = {"Authorization": f"Bearer {access_token_normal_user}"}
    body, status = await make_post_request("/role/create", headers=headers)
    assert status == HTTPStatus.FORBIDDEN
    assert body["detail"] == "Access forbidden: Superuser required"


@pytest.mark.asyncio(loop_scope="session")
async def test_request_creates_role(access_token_super_user, make_post_request, get_role_by_title):
    data = {"title": "created_role"}

    db_role_before = await get_role_by_title(data["title"])
    assert db_role_before is None

    headers = {"Authorization": f"Bearer {access_token_super_user}"}
    body, status = await make_post_request("/role/create", headers=headers, data=data)

    assert status == HTTPStatus.OK
    assert "id" in body
    assert body["title"] == data["title"]

    db_role_after = await get_role_by_title(data["title"])
    assert db_role_after is not None
