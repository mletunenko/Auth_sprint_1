import redis
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, HTTPException, Response, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.postgres import pg_helper
from db.redis import get_redis_connection
from models import User
from schemas.token import TokenInfo
from schemas.user import UserBaseOut, UserIn, UserLogin, UserAccountOut
from services.token import invalidate_token
from services.users import create_user as services_create_user
from services.users import validate_auth_user_login
from services.account import account_page as service_account_page

router = APIRouter()
auth_bearer = AuthJWTBearer()


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


@router.post("/login", response_model=TokenInfo)
async def login(
        user: UserLogin,
        session: AsyncSession = Depends(pg_helper.session_getter),
        authorize: AuthJWT = Depends(auth_bearer),
) -> TokenInfo:
    validated_user = await validate_auth_user_login(user, session)
    access_token = await authorize.create_access_token(subject=str(validated_user.id))
    refresh_token = await authorize.create_refresh_token(subject=str(validated_user.id))
    return TokenInfo(access=access_token, refresh=refresh_token)


@router.post("/refresh")
async def refresh(
        authorize: AuthJWT = Depends(auth_bearer),
) -> TokenInfo:
    try:
        await authorize.jwt_refresh_token_required()
        current_user = await authorize.get_jwt_subject()
        new_access_token = await authorize.create_access_token(subject=current_user)
        return TokenInfo(access=new_access_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token invalid")


@router.post("/logout")
async def logout(
        authorize: AuthJWT = Depends(auth_bearer),
        redis: redis.Redis = Depends(get_redis_connection)
) -> Response:
    try:
        await authorize.jwt_required()
        token = await authorize.get_raw_jwt()
        if await invalidate_token(token, redis):
            return Response(status_code=200)
    except ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Request cannot be completed"
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid"
        )


@router.get("/me", response_model=UserAccountOut)
async def account_page(
    session: AsyncSession = Depends(pg_helper.session_getter),
    authorize: AuthJWT = Depends(auth_bearer),
) -> UserAccountOut:
    """
    Эндпоинт для страницы Личный кабине
    Доступен только для аутентифицированных юзеров
    Достает id из JWT токена, и возвращает модель
    """
    await authorize.jwt_required()
    user_id = await authorize.get_jwt_subject()
    user = await service_account_page(user_id=user_id, session=session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
