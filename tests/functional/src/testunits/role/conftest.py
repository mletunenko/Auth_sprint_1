import pytest_asyncio


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def role_endpoints(normal_role, normal_user):
    endpoints = {
        "/role/list": "get",
        "/role/create": "post",
        f"/role/update/{normal_role.id}": "post",
        f"/role/delete/{normal_role.id}": "delete",
        f"/role/{normal_role.id}/assign/{normal_user.id}": "post",
        f"/role/revoke/{normal_user.id}": "post",
    }
    yield endpoints
