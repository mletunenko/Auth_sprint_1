import aiohttp
import pytest_asyncio
from async_fastapi_jwt_auth import AuthJWT
from fastapi.params import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.settings import redis_settings, webapp_settings


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_db_session():
    pass


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def make_get_request(http_client: aiohttp.ClientSession):

    async def inner(endpoint: str, query_data: dict | None = None):
        url = webapp_settings.service_url + endpoint
        response = await http_client.get(url, params=query_data)
        body = await response.json()
        status = response.status
        return body, status

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def redis_client():
    r = Redis(host=redis_settings.redis_host, port=redis_settings.redis_port)
    yield r
    await r.aclose()


@pytest_asyncio.fixture(scope="function", loop_scope="session", autouse=True)
async def clear_cache(redis_client: Redis):
    yield
    await redis_client.flushdb()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def clear_cache_by_prefix(redis_client: Redis):

    async def inner(prefix):
        pattern = f"{prefix}:*"
        async for key in redis_client.scan_iter(pattern):
            await redis_client.delete(key)

    return inner


# Фикстура для авторизации
@pytest_asyncio.fixture(scope="session", loop_scope="session")
def access_token(test_user):
    jwt = AuthJWT()
    return jwt.create_access_token(subject=str(test_user.id))


# Фикстура для тестового пользователя
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_user(test_db_session):
    pass
