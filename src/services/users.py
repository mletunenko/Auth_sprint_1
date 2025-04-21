from fastapi import HTTPException, status
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import User
from schemas.user import UserIn, UserListParams, UserOut, UserPatch


async def get_user_by_id(user_id: UUID4, session: AsyncSession) -> UserOut | None:
    """
    Метод возвращяет данные по юзеру по его id
    """
    stmt = select(User).where(User.id == user_id)

    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        return None

    return user


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
) -> list[User]:
    stmt = select(User)
    if query_params.email:
        stmt = stmt.filter(User.email == query_params.email)

    stmt = stmt.offset((query_params.pagination.page_number - 1) * query_params.pagination.page_size).limit(
        query_params.pagination.page_size
    )
    result = await session.execute(stmt)
    user_list = result.scalars().all()
    return user_list


async def service_user_delete(
    user_id: UUID4,
    session: AsyncSession,
) -> None:
    user = await get_user_by_id(user_id, session)
    await session.delete(user)
    await session.commit()


async def service_user_patch(
    user_id: UUID4,
    data: UserPatch,
    session: AsyncSession,
) -> User:
    user = await get_user_by_id(user_id, session)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "email":
            stmt = select(User).where(User.email == update_data["email"]).where(User.id != str(user_id))
            result = await session.execute(stmt)
            existing_user = result.scalars().first()
            if existing_user:
                raise HTTPException(status_code=400, detail="User with this username or email already exists")

        elif field == "password":
            setattr(user, field, pbkdf2_sha256.hash(value))
        else:
            setattr(user, field, value)
    await session.commit()
    return user
