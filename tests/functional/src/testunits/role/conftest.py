import uuid
import datetime

import pytest_asyncio
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from sqlalchemy import Table, Column, String, Boolean, DateTime, delete, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import insert, select


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
    normal_role = {
        "id": uuid.uuid4(),
        "title": "normal",
        "created_at": datetime.datetime.now(datetime.timezone.utc),
    }
    async with db_session_factory() as session:
        await session.execute(insert(roles_table).values(normal_role))
        await session.commit()
        result = await session.execute(
            select(roles_table).where(roles_table.c.title == normal_role["title"])
        )
        role = result.fetchone()
        yield role


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def create_role(db_session_factory, roles_table):
    async def inner(title: str):
        role = {
            "id": uuid.uuid4(),
            "title": title,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }
        async with db_session_factory() as session:
            await session.execute(insert(roles_table).values(role))
            await session.commit()

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def create_user(db_session_factory, users_table):
    async def inner(email: str):
        user = {
            "id": uuid.uuid4(),
            "email": email,
            "password": pbkdf2_sha256.hash("hashedpassword123"),
            "first_name": "Test",
            "last_name": "User",
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "updated_at": datetime.datetime.now(datetime.timezone.utc),
        }
        async with db_session_factory() as session:
            await session.execute(insert(users_table).values(user))
            await session.commit()
        return user

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def assign_role_to_user(db_session_factory, users_table):
    async def inner(user_id: str, role_id: str):

        async with db_session_factory() as session:
            stmt = update(users_table).where(users_table.c.id == user_id).values(role_id=role_id)
            await session.execute(stmt)
            await session.commit()

    return inner


@pytest_asyncio.fixture(scope="function", loop_scope="session")
def get_user_by_email(db_session_factory, users_table):
    async def inner(email: str):
        async with db_session_factory() as session:
            result = await session.execute(select(users_table).where(users_table.c.email == email))
            user = result.one_or_none()
        return user

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def list_roles(db_session_factory, roles_table):
    async def inner():
        async with db_session_factory() as session:
            result = await session.execute(select(roles_table))
            role = result.scalars().all()
        return role

    return inner


@pytest_asyncio.fixture(scope="function", loop_scope="session")
def get_role_by_title(db_session_factory, roles_table):
    async def inner(title: str):
        async with db_session_factory() as session:
            result = await session.execute(select(roles_table).where(roles_table.c.title == title))
            role = result.one_or_none()
        return role

    return inner


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


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def clear_roles(db_session_factory, roles_table):
    yield
    async with db_session_factory() as session:
        await session.execute(delete(roles_table).where(roles_table.c.system_role == False))
        await session.commit()
