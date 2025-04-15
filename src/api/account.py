from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, Depends, HTTPException, Query, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from db.redis import get_redis_connection
from schemas.account import LoginHistoryOut
from services.account import get_login_history
from services.token import check_invalid_token

from .dependencies import get_session

router = APIRouter()
auth_bearer = AuthJWTBearer()


# @router.patch("/update")
# async def update_user(
#     user_update: UserRegisterIn,
#     session: AsyncSession = Depends(get_session),
#     authorize: AuthJWT = Depends(auth_bearer),
#     redis: Redis = Depends(get_redis_connection),
# ) -> dict:
#     """
#     Эндпоинт для изменения информации о юзере
#     """
#     await authorize.jwt_required()
#     token = await authorize.get_raw_jwt()
#     if await check_invalid_token(token, redis):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")
#
#     user_id: UUID4 = await authorize.get_jwt_subject()
#
#     return await update_user_data(
#         user_id,
#         user_update,
#         session,
#     )


@router.get("/history", response_model=LoginHistoryOut)
async def get_history(
    authorize: AuthJWT = Depends(auth_bearer),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_connection),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
) -> LoginHistoryOut:
    """
    Эндпоинт для просмотра истории входов пользователя
    """
    await authorize.jwt_required()

    token = await authorize.get_raw_jwt()
    if await check_invalid_token(token, redis):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")

    user_id = await authorize.get_jwt_subject()

    history = await get_login_history(user_id, page, page_size, session)
    return history
