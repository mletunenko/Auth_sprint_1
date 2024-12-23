from http import HTTPStatus

import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_token_required_to_access_view(normal_user, make_post_request):
    _, status = await make_post_request(f"/role/revoke/{normal_user.id}")
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_superuser_required_in_token_claims(
    normal_user, access_token_normal_user, make_post_request
):
    headers = {"Authorization": f"Bearer {access_token_normal_user}"}
    body, status = await make_post_request(f"/role/revoke/{normal_user.id}", headers=headers)
    assert status == HTTPStatus.FORBIDDEN
    assert body["detail"] == "Access forbidden: Superuser required"


@pytest.mark.asyncio(loop_scope="session")
async def test_request_revokes_role(
    create_role,
    get_role_by_title,
    create_user,
    assign_role_to_user,
    get_user_by_email,
    access_token_super_user,
    make_post_request,
):
    role_data = {"title": "role to revoke"}
    await create_role(role_data["title"])
    role = await get_role_by_title(role_data["title"])

    user_data = {"email": "revoke@test.com"}
    user = await create_user(user_data["email"])
    await assign_role_to_user(user["id"], role.id)
    user_before = await get_user_by_email(user_data["email"])

    assert user_before.role_id == role.id

    headers = {"Authorization": f"Bearer {access_token_super_user}"}
    _, status = await make_post_request(f"/role/revoke/{user_before.id}", headers=headers)

    assert status == HTTPStatus.OK

    user_after = await get_user_by_email(user_data["email"])
    assert user_after.role_id is None
