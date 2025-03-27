import aiohttp
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings
from models import User
from schemas.user import UserListParams, UserLoginIn, UserRegisterIn


async def create_user(
    user_create: UserRegisterIn,
    session: AsyncSession,
) -> User:
    user = User(**user_create.model_dump())
    user.set_password(user_create.password)
    session.add(user)
    await session.commit()

    url = f"http://{settings.notification_server.host}:{settings.notification_server.port}{settings.notification_server.welcome_path}?user_id={user.id}"
    async with aiohttp.ClientSession() as session:
        await session.post(url)

    return user


async def validate_auth_user_login(
    user: UserLoginIn,
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
    if query_params.birth_date:
        stmt = stmt.where(User.birth_date == query_params.birth_date)
    stmt = stmt.offset((query_params.pagination.page_number - 1) * query_params.pagination.page_size).limit(
        query_params.pagination.page_size
    )
    result = await session.execute(stmt)
    user_list = result.scalars().all()
    return user_list
