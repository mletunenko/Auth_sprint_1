from sqlalchemy.ext.asyncio import AsyncSession

from models import User
from schemas.user import UserCreate, UserBase


async def create_user(
        user_create: UserCreate,
        session: AsyncSession,
) -> UserBase:
    user = User(**user_create.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user