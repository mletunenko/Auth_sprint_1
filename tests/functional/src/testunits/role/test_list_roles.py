from http import HTTPStatus

import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_token_required_to_access_view(make_get_request):
    _, status = await make_get_request("/role/list")
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_superuser_required_in_token_claims(access_token_normal_user, make_get_request):
    headers = {"Authorization": f"Bearer {access_token_normal_user}"}
    body, status = await make_get_request("/role/list", headers=headers)
    assert status == HTTPStatus.FORBIDDEN
    assert body["detail"] == "Access forbidden: Superuser required"


@pytest.mark.asyncio(loop_scope="session")
async def test_request_lists_roles(
    create_role, list_roles, access_token_super_user, make_get_request
):
    await create_role("some role")
    db_roles = await list_roles()

    assert len(db_roles) > 0
    headers = {"Authorization": f"Bearer {access_token_super_user}"}
    body, status = await make_get_request("/role/list", headers=headers)

    assert status == HTTPStatus.OK
    assert type(body) == list
    assert len(body) > 0
    assert type(body[0]) == dict

    for k in body[0].keys():
        assert k in ["id", "title"]
