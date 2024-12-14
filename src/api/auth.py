from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import pg_helper
from models import User
from schemas.user import UserBaseOut, UserIn
from services.users import create_user as services_create_user

router = APIRouter()

@router.post("/register", response_model=UserBaseOut)
async def create_user(
        user_create: UserIn,
        session: AsyncSession = Depends(pg_helper.session_getter),
) -> UserBaseOut:
    result = await session.execute(select(User).where(or_(User.login == user_create.login,User.email == user_create.email)))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this username or email already exists"
        )
    user = await services_create_user(
        user_create=user_create,
        session=session,
    )
    return user