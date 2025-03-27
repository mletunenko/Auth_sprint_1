from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_session
from schemas.user import UserAccountOut, UserListParams
from services.account import account_page as service_account_page
from services.users import service_user_list

router = APIRouter(tags=["users"])


@router.get("/users/{user_id}", response_model=UserAccountOut, summary="Информация о user по id")
async def get_user(
    user_id: UUID4,
    session: AsyncSession = Depends(get_session),
) -> UserAccountOut:
    user = await service_account_page(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/", summary="Список пользователей")
async def list_users(
    session: AsyncSession = Depends(get_session), query_params: UserListParams = Depends()
) -> list[UserAccountOut]:
    user_list = await service_user_list(session, query_params)
    response = [UserAccountOut.model_validate(user, from_attributes=True) for user in user_list]
    return response
