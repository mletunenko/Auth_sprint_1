from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import settings
from db.postgres import pg_helper
from models import User
from schemas.user import UserBaseOut, UserIn, UserLogin
from services.users import create_user as services_create_user

router = APIRouter()

http_bearer = HTTPBearer()

# Настройки конфигурации JWT
class Settings(BaseModel):
    authjwt_secret_key: str = settings.authjwt_secret_key  # Замените на ваш секретный ключ
    algorithm: str = 'RS256'

# Передача конфигурации библиотеке AuthJWT
@AuthJWT.load_config
def get_config():
    return Settings()

@router.post("/register", response_model=UserBaseOut)
async def create_user(
        user_create: UserIn,
        session: AsyncSession = Depends(pg_helper.session_getter),
) -> UserBaseOut:
    result = await session.execute(select(User).where(User.email == user_create.email))
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

async def get_user_by_email(
        email: str,
        session: AsyncSession,
) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    return user

async def validate_auth_user_login(
        email: str,
        password: str,
        session: AsyncSession = Depends(pg_helper.session_getter)
):
    unauth_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='invalid username or password'
    )
    if not (user := await get_user_by_email(email, session=session)):
        raise unauth_exc
    if not user.check_password(password):
        raise unauth_exc
    return user

@router.post('/login')
async def login(
        user: UserLogin = Depends(validate_auth_user_login),
        Authorize: AuthJWT = Depends(),
):
    access_token = await Authorize.create_access_token(subject=str(user.id))
    refresh_token = await Authorize.create_refresh_token(subject=str(user.id))
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post('/refresh')
async def refresh(
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
        Authorize: AuthJWT = Depends(),
):
    try:
        await Authorize.jwt_refresh_token_required()
        current_user = await Authorize.get_jwt_subject()
        new_access_token = await Authorize.create_access_token(subject=current_user)
        return {"access_token": new_access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail="Refresh token invalid")
