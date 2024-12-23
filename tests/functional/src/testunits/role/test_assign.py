from http import HTTPStatus

import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_token_required_to_access_view(normal_user, normal_role, make_post_request):
    _, status = await make_post_request(f"/role/{normal_role.id}/assign/{normal_user.id}")
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_superuser_required_in_token_claims(
    normal_user, normal_role, access_token_normal_user, make_post_request
):
    headers = {"Authorization": f"Bearer {access_token_normal_user}"}
    body, status = await make_post_request(
        f"/role/{normal_role.id}/assign/{normal_user.id}", headers=headers
    )
    assert status == HTTPStatus.FORBIDDEN
    assert body["detail"] == "Access forbidden: Superuser required"


@pytest.mark.asyncio(loop_scope="session")
async def test_request_assigns_role(
    create_role,
    get_role_by_title,
    create_user,
    get_user_by_email,
    access_token_super_user,
    make_post_request,
):
    role_data = {"title": "role to assign"}
    await create_role(role_data["title"])
    role = await get_role_by_title(role_data["title"])

    user_data = {"email": "assign@test.com"}
    await create_user("assign@test.com")
    user_before = await get_user_by_email(user_data["email"])

    assert user_before.role_id is None

    headers = {"Authorization": f"Bearer {access_token_super_user}"}
    _, status = await make_post_request(f"/role/{role.id}/assign/{user_before.id}", headers=headers)

    assert status == HTTPStatus.OK

    user_after = await get_user_by_email(user_data["email"])
    assert role.id == user_after.role_id
