from async_fastapi_jwt_auth.auth_jwt import AuthJWT, AuthJWTBearer
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED

from api.dependencies import get_session
from db.rabbit import RabbitDep
from db.redis import get_redis_connection
from schemas.user import UserIn, UserListParams, UserOut, UserPatch
from services.token import check_invalid_token
from services.users import (
    get_user_by_id,
    service_create_user,
    service_user_delete,
    service_user_list,
    service_user_patch,
)
from sync.tasks import update_profile_email_task

router = APIRouter(tags=["users"])
auth_bearer = AuthJWTBearer()


@router.get("/users/{user_id}", summary="Информация о user по id")
async def get_user(
    user_id: UUID4,
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/users/{user_id}", summary="Обновить данные юзера")
async def update_user(
    user_id: UUID4,
    data: UserPatch,
    rabbit_channel: RabbitDep,
    session: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_bearer),
    redis: Redis = Depends(get_redis_connection),
) -> UserOut:
    await authorize.jwt_required()
    token = await authorize.get_raw_jwt()
    if await check_invalid_token(token, redis):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token invalid")

    token_user_id: UUID4 = await authorize.get_jwt_subject()
    if not token_user_id == str(user_id):
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Token invalid")

    user = await get_user_by_id(user_id, session)
    old_email = user.email

    user = await service_user_patch(user_id, data, session)

    if hasattr(data, "email") and old_email != data.email:
        await update_profile_email_task(old_email, data.email, rabbit_channel)

    return user


@router.get("/users/", summary="Список пользователей")
async def list_users(
    session: AsyncSession = Depends(get_session), query_params: UserListParams = Depends()
) -> list[UserOut]:
    user_list = await service_user_list(session, query_params)
    return user_list


@router.post("/users/", summary="Создать пользователя")
async def create_user(
    user_data: UserIn,
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    user = await service_create_user(user_data, session)
    return user


@router.delete("/users/{user_id}", summary="Удалить юзера")
async def delete_user(
    user_id: UUID4,
    session: AsyncSession = Depends(get_session),
) -> Response:
    await service_user_delete(user_id, session)
    return Response(status_code=HTTP_204_NO_CONTENT)
