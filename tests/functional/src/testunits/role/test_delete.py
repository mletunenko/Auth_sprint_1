from http import HTTPStatus

import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_token_required_to_access_view(normal_user, make_delete_request):
    _, status = await make_delete_request(f"/role/delete/{normal_user.id}")
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_superuser_required_in_token_claims(
    normal_user, access_token_normal_user, make_delete_request
):
    headers = {"Authorization": f"Bearer {access_token_normal_user}"}
    body, status = await make_delete_request(f"/role/delete/{normal_user.id}", headers=headers)
    assert status == HTTPStatus.FORBIDDEN
    assert body["detail"] == "Access forbidden: Superuser required"


@pytest.mark.asyncio(loop_scope="session")
async def test_request_delete_role(
    create_role, get_role_by_title, access_token_super_user, make_delete_request
):
    await create_role("role to delete")
    db_role_before = await get_role_by_title("role to delete")
    assert db_role_before is not None

    headers = {"Authorization": f"Bearer {access_token_super_user}"}
    body, status = await make_delete_request(f"/role/delete/{db_role_before.id}", headers=headers)

    assert status == HTTPStatus.OK
    db_role_after = await get_role_by_title("role to delete")
    assert db_role_after is None
