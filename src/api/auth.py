from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import pg_helper
from async_fastapi_jwt_auth import AuthJWT

from api.basic import auth_dep
from schemas.user import UserBaseOut, UserCreateIn, UserAccountOut
from services.users import create_user as services_create_user
from services.account import account_page as service_account_page


router = APIRouter()


@router.post("/register", response_model=UserBaseOut)
async def create_user(
        user_create: UserCreateIn,
        session: AsyncSession = Depends(pg_helper.session_getter),
) -> UserBaseOut:
    user = await services_create_user(
        user_create=user_create,
        session=session,
    )
    return user


@router.get("/me", response_model=UserAccountOut)
async def account_page(
    session: AsyncSession = Depends(pg_helper.session_getter),
    authorize: AuthJWT = Depends(auth_dep),
) -> UserAccountOut:
    """
    Эндпоинт для страницы Личный кабине
    Доступен только для аутентифицированных юзеров
    Достает id из JWT токена, и возвращает модель
    """
    await authorize.jwt_required()
    user_id = await authorize.get_jwt_subject()
    user = await service_account_page(user_id=user_id, session=session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
