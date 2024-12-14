from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserAccountOut
from pydantic import UUID4


async def account_page(
        user_id: UUID4,
        session: AsyncSession,
) -> UserAccountOut:
    # TODO доделать запрос
    user = session.get(user_id)
    await session.commit()
    return user
