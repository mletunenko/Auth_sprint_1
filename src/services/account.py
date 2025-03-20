from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from models import LoginHistory, User
from schemas.account import HistoryItem, HistoryMeta, LoginHistoryOut
from schemas.user import UserAccountOut, UserRegisterIn
from services.users import get_user_by_email


async def account_page(user_id: UUID4, session: AsyncSession) -> UserAccountOut | None:
    """
    Метод возвращяет данные по юзеру по его id
    """
    stmt = select(User).where(User.id == user_id)

    result = await session.execute(stmt)
    user = result.scalars().first()

    if not user:
        return None

    return UserAccountOut(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        birth_date=user.birth_date,
    )


async def get_login_history(
    user_id: UUID4,
    page: int,
    page_size: int,
    session: AsyncSession,
):
    total_count_query = select(func.count(LoginHistory.id)).where(LoginHistory.user_id == user_id)
    total_count = (await session.execute(total_count_query)).scalar()

    query = (
        select(LoginHistory)
        .where(LoginHistory.user_id == user_id)
        .order_by(LoginHistory.timestamp.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.execute(query)
    login_history = result.scalars().all()

    history_data = [
        HistoryItem(
            date_time=lh.timestamp.strftime("%a %d %b %Y, %I:%M%p"), ip_address=lh.ip_address, user_agent=lh.user_agent
        )
        for lh in login_history
    ]

    meta = HistoryMeta(
        current_page=page,
        page_size=page_size,
        total_count=total_count,
        total_pages=(total_count + page_size - 1) // page_size,
    )

    return LoginHistoryOut(
        data=history_data,
        meta=meta,
    )


async def update_user_data(
    user_id: UUID4,
    user_update: UserRegisterIn,
    session: AsyncSession,
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Проверка уникальности email
    if user.email != user_update.email:
        existing_user = await get_user_by_email(
            user_update.email,
            session,
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this username or email already exists")

    # Обновление данных
    user.email = user_update.email
    user.set_password(user_update.password)
    user.first_name = user_update.first_name
    user.last_name = user_update.last_name
    user.birth_date = user_update.birth_date

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Error updating user information")
    return {"detail": "User information updated successfully"}
