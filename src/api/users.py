from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_session
from schemas.user import UserIn, UserListParams, UserOut
from services.account import account_page as service_account_page
from services.users import service_create_user, service_user_list

router = APIRouter(tags=["users"])


@router.get("/users/{user_id}", summary="Информация о user по id")
async def get_user(
    user_id: UUID4,
    session: AsyncSession = Depends(get_session),
) -> UserOut:
    user = await service_account_page(user_id, session)
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
