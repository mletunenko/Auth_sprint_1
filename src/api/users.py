from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_session
from schemas.user import UserAccountOut
from services.account import account_page as service_account_page

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
