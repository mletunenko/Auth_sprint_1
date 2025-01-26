from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserAccountOut, UserLoginIn


async def account_page(
    user_id: UUID4,
    session: AsyncSession
) -> UserAccountOut:
    """
    Метод возвращяет данные по юзеру по его id
    """
    stmt = select(User).where(User.id == user_id)

    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        return None

    return UserLoginIn(
        email=user.email,
        password="***********"
    )
