from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from starlette.status import HTTP_204_NO_CONTENT

from api.dependencies import get_session
from schemas.user import UserIn, UserListParams, UserOut, UserPatch
from services.users import service_create_user, service_user_list, get_user_by_id, service_user_delete, \
    service_user_patch

router = APIRouter(tags=["users"])


@router.get("/users/{user_id}", summary="Информация о user по id")
async def get_user(
    user_id: UUID4,
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    user = await get_user_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/", summary="Список пользователей")
async def list_users(
    session: AsyncSession = Depends(get_session), query_params: UserListParams = Depends()
) -> list[UserOut]:
    user_list = await service_user_list(session, query_params)
    return user_list


@router.post("/users/", summary="Создать пользователя")
async def create_user(user_data: UserIn, session: AsyncSession = Depends(get_session)) -> UserOut:
    user = await service_create_user(user_data, session)
    return user

@router.delete("/users/{user_id}", summary="Удалить юзера")
async def delete_user(
        user_id: UUID4,
        session: AsyncSession = Depends(get_session),
) -> Response:
    await service_user_delete(user_id, session)
    return Response(status_code=HTTP_204_NO_CONTENT)

@router.patch("/users/{user_id}", summary="Обновить данные юзера")
async def update_user(
        user_id: UUID4,
        data: UserPatch,
        session: AsyncSession = Depends(get_session),
) -> UserOut:
    user = await service_user_patch(user_id, data, session)
    return user
