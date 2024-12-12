from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import pg_helper
from schemas.user import UserBaseOut, UserCreateIn
from services.users import create_user as services_create_user

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