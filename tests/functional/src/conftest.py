import uuid
import datetime

import aiohttp
import pytest_asyncio
from async_fastapi_jwt_auth import AuthJWT
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from redis.asyncio import Redis
from sqlalchemy import MetaData, Table, Column, String, Boolean, DateTime, ForeignKey, delete
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.sql import insert, select

from settings import redis_settings, pg_settings, webapp_settings


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def make_get_request(http_client: aiohttp.ClientSession):

    async def inner(endpoint: str, headers={}, query_data: dict | None = None):
        url = webapp_settings.service_url + endpoint
        response = await http_client.get(url, headers=headers, params=query_data)
        try:
            body = await response.json()
        except aiohttp.ContentTypeError:
            body = await response.text()
        status = response.status
        return body, status

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def make_post_request(http_client: aiohttp.ClientSession):

    async def inner(endpoint: str, headers={}, data: dict = {}):
        url = webapp_settings.service_url + endpoint
        response = await http_client.post(url, headers=headers, json=data)
        try:
            body = await response.json()
        except aiohttp.ContentTypeError:
            body = await response.text()
        status = response.status
        return body, status

    return inner


# Фикстура для авторизации
@pytest_asyncio.fixture(scope="session", loop_scope="session")
def access_token(test_user):
    jwt = AuthJWT()
    return jwt.create_access_token(subject=str(test_user.id))


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


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db_session_factory():
    engine = create_async_engine(url=str(pg_settings.pg_url))
    session_factory = async_sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    yield session_factory
    await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def table_metadata():
    metadata = MetaData()
    yield metadata


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def users_table(table_metadata):
    users_table = Table(
        "users",
        table_metadata,
        Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column("email", String, unique=True, nullable=False),
        Column("password", String, nullable=False),
        Column("first_name", String, nullable=False, default=""),
        Column("last_name", String, nullable=False, default=""),
        Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), nullable=True),
        Column(
            "created_at",
            DateTime(timezone=True),
            default=datetime.datetime.now(datetime.timezone.utc),
        ),
        Column(
            "updated_at",
            DateTime(timezone=True),
            onupdate=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    return users_table


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def roles_table(table_metadata):
    roles_table = Table(
        "roles",
        table_metadata,
        Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column("title", String, unique=True, nullable=False),
        Column("system_role", Boolean, default=False),
        Column(
            "created_at",
            DateTime(timezone=True),
            default=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    return roles_table


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def normal_role(db_session_factory, roles_table):
    async with db_session_factory() as session:
        result = await session.execute(
            select(roles_table).where(roles_table.c.title == "regular user")
        )
        role = result.fetchone()
        yield role


# Фикстура для тестового пользователя
@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def normal_user(db_session_factory, users_table, normal_role):
    user = {
        "id": uuid.uuid4(),
        "email": "regular_user@example.com",
        "password": pbkdf2_sha256.hash("hashedpassword123"),
        "first_name": "Regular",
        "last_name": "User",
        "role_id": normal_role.id,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc),
    }
    async with db_session_factory() as session:
        await session.execute(insert(users_table).values(user))
        await session.commit()

        result = await session.execute(
            select(users_table).where(users_table.c.email == "regular_user@example.com")
        )
        db_user = result.fetchone()
        yield db_user
        await session.execute(
            delete(users_table).where(users_table.c.email == "regular_user@example.com")
        )
        await session.commit()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def super_role(db_session_factory, roles_table):
    async with db_session_factory() as session:
        result = await session.execute(
            select(roles_table).where(roles_table.c.title == "superuser")
        )
        role = result.fetchone()
        yield role


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def super_user(db_session_factory, users_table, super_role):
    user = {
        "id": uuid.uuid4(),
        "email": "superuser@example.com",
        "password": pbkdf2_sha256.hash("hashedpassword456"),
        "first_name": "Super",
        "last_name": "User",
        "role_id": super_role.id,
        "created_at": datetime.datetime.now(datetime.timezone.utc),
        "updated_at": datetime.datetime.now(datetime.timezone.utc),
    }
    async with db_session_factory() as session:
        await session.execute(insert(users_table).values(user))
        await session.commit()

        result = await session.execute(
            select(users_table).where(users_table.c.email == "superuser@example.com")
        )
        db_user = result.fetchone()
        yield db_user

        await session.execute(
            delete(users_table).where(users_table.c.email == "superuser@example.com")
        )
        await session.commit()
