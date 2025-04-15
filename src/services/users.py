import aiohttp
from fastapi import HTTPException, status
from sqlalchemy import extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings
from models import User
from schemas.user import UserIn, UserListParams


async def service_create_user(
    user_create: UserIn,
    session: AsyncSession,
) -> User:
    existing_user = await get_user_by_email(
        user_create.email,
        session,
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")
    user = User(**user_create.model_dump())
    user.set_password(user_create.password)
    session.add(user)
    await session.commit()

    url = f"http://{settings.notification_server.host}:{settings.notification_server.port}{settings.notification_server.welcome_path}?user_id={user.id}"
    async with aiohttp.ClientSession() as session:
        await session.post(url)

    return user


async def validate_auth_user_login(
    user: UserIn,
    session: AsyncSession,
) -> User:
    """
    Проверка, что юзер существует в БД и указан правильный пароль
    """
    email, password = user.email, user.password
    unauth_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid username or password")
    if not (user := await get_user_by_email(email, session=session)):
        raise unauth_exc
    if not user.check_password(password):
        raise unauth_exc
    return user


async def get_user_by_email(
    email: str,
    session: AsyncSession,
) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    existing_user = result.scalars().first()
    return existing_user


async def service_user_list(
    session: AsyncSession,
    query_params: UserListParams,
):
    stmt = select(User)
    if query_params.birth_day:
        stmt = stmt.filter(extract("day", User.birth_date) == query_params.birth_day)

    if query_params.birth_month:
        stmt = stmt.filter(extract("month", User.birth_date) == query_params.birth_month)

    stmt = stmt.offset((query_params.pagination.page_number - 1) * query_params.pagination.page_size).limit(
        query_params.pagination.page_size
    )
    result = await session.execute(stmt)
    user_list = result.scalars().all()
    return user_list
