from http import HTTPStatus

import pytest
import pytest_asyncio


@pytest.mark.asyncio(loop_scope="session")
async def test_token_required_to_access_view(normal_role, make_post_request):
    _, status = await make_post_request(f"/role/update/{normal_role.id}")
    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio(loop_scope="session")
async def test_superuser_required_in_token_claims(
    normal_role, access_token_normal_user, make_post_request
):
    headers = {"Authorization": f"Bearer {access_token_normal_user}"}
    body, status = await make_post_request(f"/role/update/{normal_role.id}", headers=headers)
    assert status == HTTPStatus.FORBIDDEN
    assert body["detail"] == "Access forbidden: Superuser required"


@pytest.mark.asyncio(loop_scope="session")
async def test_request_updates_role(
    access_token_super_user, make_post_request, create_role, get_role_by_title
):
    data = {"title": "update_role_before"}
    await create_role(data["title"])
    db_role_before = await get_role_by_title(data["title"])
    assert db_role_before.title == data["title"]

    headers = {"Authorization": f"Bearer {access_token_super_user}"}
    new_data = {"title": "update_role_after"}
    _, status = await make_post_request(
        f"/role/update/{db_role_before.id}", headers=headers, data=new_data
    )

    assert status == HTTPStatus.OK

    db_role_after = await get_role_by_title(new_data["title"])
    assert db_role_before.id == db_role_after.id
    assert db_role_after.title != data["title"]
    assert db_role_after.title == new_data["title"]
