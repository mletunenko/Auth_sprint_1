from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import pg_helper
from schemas.user import UserCreate, UserBase
from services.users import create_user as services_create_user

router = APIRouter()

@router.post("/register/", response_model=UserBase)
async def create_user(
        user_create: UserCreate,
        session: AsyncSession = Depends(pg_helper.session_getter),
) -> UserBase:
    user = await services_create_user(
        user_create=user_create,
        session=session,
    )
    return user