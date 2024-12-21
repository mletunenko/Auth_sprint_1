from typing import Dict, List

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import pg_helper
from models.history import LoginHistory
from models.user import User
from schemas.user import UserLogin, UserUpdate
from services.account import account_page as service_account_page

router = APIRouter()
auth_bearer = AuthJWTBearer()


@router.patch("/update")
async def update_user(
        user_update: UserUpdate,
        session: AsyncSession = Depends(pg_helper.session_getter),
        authorize: AuthJWT = Depends(auth_bearer),
) -> dict:
    """
    Эндпоинт для изменения почты или пароля
    """

    await authorize.jwt_required()
    user_id: UUID4 = await authorize.get_jwt_subject()

    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Проверка уникальности email
    if user.email != user_update.email:
        result = await session.execute(
            select(User).where(User.email == user_update.email)
        )
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")

    # Обновление данных
    user.email = user_update.email
    user.set_password(user_update.password)

    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=400, detail="Error updating user information"
        )

    return {"detail": "User information updated successfully"}


@router.get("/me", response_model=UserLogin)
async def account_page(
    session: AsyncSession = Depends(pg_helper.session_getter),
    authorize: AuthJWT = Depends(auth_bearer),
) -> UserLogin:
    """
    Эндпоинт для страницы Личный кабинет
    Доступен только для аутентифицированных юзеров
    Достает id из JWT токена, и возвращает модель
    """
    await authorize.jwt_required()
    user_id: UUID4 = await authorize.get_jwt_subject()
    user: UserLogin = await service_account_page(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/history", response_model=List[Dict[str, str]])
async def get_login_history(
        authorize: AuthJWT = Depends(auth_bearer),
        session: AsyncSession = Depends(pg_helper.session_getter)
) -> List[Dict[str, str]]:
    """
    Эндпоинт для просмотра истории входов пользователя
    """

    await authorize.jwt_required()

    # Получение идентификатора пользователя из токена
    user_id: UUID4 = await authorize.get_jwt_subject()

    # Запрос истории входов из базы данных
    result = await session.execute(
        select(LoginHistory).where(
            LoginHistory.user_id == user_id
        ).order_by(LoginHistory.timestamp.desc())
    )
    login_history = result.scalars().all()

    # Форматирование данных для ответа
    return [{
        "date_time": lh.timestamp.strftime('%a %d %b %Y, %I:%M%p'),
        "ip_address": lh.ip_address,
        "user-agent": lh.user_agent
        } for lh in login_history]
