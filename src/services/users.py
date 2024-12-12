from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserCreateIn


async def create_user(
        user_create: UserCreateIn,
        session: AsyncSession,
) -> User:
    user = User(**user_create.model_dump())
    user.set_password(user_create.password)
    session.add(user)
    await session.commit()
    return user