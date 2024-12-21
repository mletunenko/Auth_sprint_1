import aiohttp
import pytest_asyncio
from async_fastapi_jwt_auth import AuthJWT
from fastapi.params import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import pg_helper
from models.user import User
from src.settings import redis_test_settings, webapp_test_settings


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def test_db_session(
    session: AsyncSession = Depends(pg_helper.session_getter)
):
    yield session


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def http_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope='session', loop_scope='session')
def make_get_request(http_client: aiohttp.ClientSession):

    async def inner(endpoint: str, query_data: dict | None = None):
        url = webapp_test_settings.service_url + endpoint
        response = await http_client.get(url, params=query_data)
        body = await response.json()
        status = response.status
        return body, status

    return inner


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def redis_client():
    r = Redis(host=redis_test_settings.redis_host,
              port=redis_test_settings.redis_port)
    yield r
    await r.aclose()


@pytest_asyncio.fixture(scope='function', loop_scope='session', autouse=True)
async def clear_cache(redis_client: Redis):
    yield
    await redis_client.flushdb()


@pytest_asyncio.fixture(scope='session', loop_scope='session')
def clear_cache_by_prefix(redis_client: Redis):

    async def inner(prefix):
        pattern = f"{prefix}:*"
        async for key in redis_client.scan_iter(pattern):
            await redis_client.delete(key)

    return inner


# Фикстура для авторизации
@pytest_asyncio.fixture(scope='session', loop_scope='session')
def access_token(test_user):
    jwt = AuthJWT()
    return jwt.create_access_token(subject=str(test_user.id))


# Фикстура для тестового пользователя
@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def test_user(test_db_session):
    user = User(email="testuser@mail.com")
    user.set_password("testpassword")
    test_db_session.add(user)
    await test_db_session.commit()
    return user