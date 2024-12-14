from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserAccountOut, UserIdOut
from pydantic import UUID4, EmailStr


async def account_page(
    user_id: UUID4,
    session: AsyncSession
) -> UserAccountOut:
    """
    Метод возвращяет данные по юзеру  юзеру по его id
    """
    stmt = select(User).where(User.id == user_id)

    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        return None

    return UserAccountOut(
        id=user.id,
        email=user.email,
        password="***********"
    )


async def get_current_user(
    email: EmailStr,
    session: AsyncSession
) -> UserIdOut:
    """
    Метод возвращяет id текущего юзера
    по его JWT токену переданному в запросе
    """
    stmt = select(User).where(User.email == email)

    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        return None

    return UserIdOut(
        id=user.id,
    )
