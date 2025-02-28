import asyncio
from logging import getLogger

import httpx
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from passlib.utils import generate_password
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from api.exceptions import Http400, Http500
from core.config import settings
from db.redis import get_redis_connection
from db.repository import AsyncBaseRepository
from models import User
from models.history import LoginHistory
from schemas.enums import ServiceWorkResults
from schemas.token import TokenInfo
from schemas.user import UserLoginIn, UserLoginOut, UserRegisterIn, UserRegisterOut
from services.oauth import get_provider_by_name, get_user_by_provider_user_id, save_oauth_account
from services.token import authorize_by_user_id, check_invalid_token, invalidate_token
from services.users import create_user as services_create_user
from services.users import get_user_by_email, validate_auth_user_login
from utils.email_generator import generate_email

from .dependencies import check_invalid_token as check_invalid_token_depcy
from .dependencies import check_superuser, get_session, get_sqlalchemy_repository

router = APIRouter()
auth_bearer = AuthJWTBearer()

logger = getLogger(__name__)


async def handle_login(
    user: User,
    request: Request,
    session: AsyncSession,
    authorize: AuthJWT,
) -> UserLoginOut:
    try:
        roles_claim = user.role.title
    except AttributeError:
        roles_claim = None

    claims = {"roles": roles_claim}
    # Создание токенов
    access_token = await authorize.create_access_token(
        subject=str(user.id), user_claims=claims, expires_time=60*30
    )
    refresh_token = await authorize.create_refresh_token(
        subject=str(user.id), user_claims=claims
    )

    # Сохранение истории входа
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    login_history = LoginHistory(
        user_id=user.id, ip_address=ip_address, user_agent=user_agent
    )
    session.add(login_history)
    await session.commit()

    user_role = user.role.title if user.role else user.role

    return UserLoginOut(access=access_token,
                        refresh=refresh_token,
                        id=user.id,
                        email=user.email,
                        role=user_role,)


@router.post("/register", response_model=UserRegisterOut)
async def create_user(
    user_create: UserRegisterIn,
    session: AsyncSession = Depends(get_session),
) -> UserRegisterOut:
    existing_user = await get_user_by_email(
        user_create.email,
        session,
    )
    if existing_user:
        raise HTTPException(
            status_code=400, detail="User with this username or email already exists"
        )
    user = await services_create_user(
        user_create=user_create,
        session=session,
    )
    existing_user = await get_user_by_email(
        user_create.email,
        session,
    )
    return user


@router.post("/login", response_model=UserLoginOut)
async def login(
    user: UserLoginIn,
    request: Request,
    session: AsyncSession = Depends(get_session),
    authorize: AuthJWT = Depends(auth_bearer),
) -> UserLoginOut:
    validated_user = await validate_auth_user_login(user, session)
    return await handle_login(
        validated_user,
        request,
        session,
        authorize
    )



@router.post("/refresh")
async def refresh(
    authorize: AuthJWT = Depends(auth_bearer),
) -> TokenInfo:
    try:
        await authorize.jwt_refresh_token_required()
        current_user = await authorize.get_jwt_subject()
        payload = await authorize.get_raw_jwt()
        new_access_token = await authorize.create_access_token(
            subject=current_user, user_claims=payload
        )
        return TokenInfo(access=new_access_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token invalid")


@router.post("/logout")
async def logout(
    authorize: AuthJWT = Depends(auth_bearer),
    redis: Redis = Depends(get_redis_connection),
) -> dict:
    try:
        await authorize.jwt_required()
        token = await authorize.get_raw_jwt()
        if await check_invalid_token(token, redis):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")
        if await invalidate_token(token, redis):
            return {"detail" : "Действие успешно выполнено"}
    except ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Request cannot be completed"
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid")


@router.post(
    "/supervised_login/{user_id}",
    dependencies=[Depends(check_invalid_token_depcy), Depends(check_superuser),]
)
async def supervised_login(
    user_id: str,
    repository: AsyncBaseRepository = Depends(get_sqlalchemy_repository),
    authorize: AuthJWT = Depends(auth_bearer)
) -> TokenInfo | None:
    result, token_pair, res_msg = await authorize_by_user_id(user_id, authorize, repository)

    if result is ServiceWorkResults.ERROR:
        raise Http500
    if result is ServiceWorkResults.FAIL:
        raise Http400(res_msg)

    return token_pair

@router.get("/social_auth")
async def social_auth(
        provider:str,
) -> RedirectResponse:
    if provider == "yandex":
        """Перенаправляет пользователя на страницу авторизации Яндекс"""
        params = {
            "response_type": "code",
            "client_id": settings.yandex_auth.client_id,
            "redirect_uri": settings.yandex_auth.redirect_uri,
        }
        redirect_url = f"{settings.yandex_auth.oauth_url}?{httpx.QueryParams(params)}"
        return RedirectResponse(url=redirect_url)
    raise HTTPException(status_code=400, detail="Неизвестный провайдер")

@router.get("/yandex_id_login/primary_redirect")
async def yandex_id_redirect_redirect(request: Request,) -> RedirectResponse:
    code = request.query_params.get("code")
    redirect_url = f"http://127.0.0.1:8000/auth/yandex_id_login/redirect?code={code}"
    return RedirectResponse(url=redirect_url)


@router.get("/yandex_id_login/redirect")
async def yandex_id_redirect(
        request: Request,
        session: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends(auth_bearer),
        redis_con: Redis = Depends(get_redis_connection)
) -> UserLoginOut:
    """
    Обрабатывает callback, создает пользователя в БД, если он не существует,
    и возвращает информацию о входе.
    """
    user = None
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Код авторизации отсутствует")

    # yandex посылает 2 запроса, а первый отменяет. фиксим это
    # sleep нужен длч того, чтобы яндекс успел отменить запрос! и мы не потратили code
    # ЭТО ЖЕСТЬ
    code_flag = await redis_con.get(f"yandex_auth_code:{code}")
    if not code_flag:
        await redis_con.set(f"yandex_auth_code:{code}", 1, ex=5 * 60)
        await asyncio.sleep(10)
        raise HTTPException(status_code=400, detail="YANDEX THROTTLE")

    async with httpx.AsyncClient() as client:
        url = settings.yandex_auth.token_url
        data = {
                "grant_type" : "authorization_code",
                "code" : code,
                "client_id" : settings.yandex_auth.client_id,
                "client_secret" : settings.yandex_auth.client_secret,
            }
        logger.info("Request to: %s, with data: %s", url, data)
        token_response = await client.post(
            url,
            data=data,
        )
        logger.info("Response from %s with status code %s: %s", url, token_response.status_code, token_response.json())
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Не удалось получить токен")

        token_data = token_response.json()
        access_token = token_data.get("access_token")

    async with httpx.AsyncClient() as client:
        data_response = await client.get(
            settings.yandex_auth.user_info_url,
            headers={
                "Authorization": f"OAuth {access_token}",
            },
        )
        if data_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Не удалось получить данные о пользователе")

        user_data =data_response.json()

        email = user_data["default_email"]
        if email:
            user = await get_user_by_email(
                email,
                session
            )
        if not user:
            user = await get_user_by_provider_user_id(
                user_data["id"],
                session,
            )
        if not user:
            user_create = UserRegisterIn(
                email=user_data.get("default_email", generate_email()),
                password=generate_password()
            )
            user = await services_create_user(
                user_create=user_create,
                session=session,
            )

        yandex_provider = await get_provider_by_name("yandex", session)

        await save_oauth_account(
            user.id,
            yandex_provider.id,
            user_data["id"],
            token_data,
            session,
        )

        result = await handle_login(
            user,
            request,
            session,
            authorize
        )
        return result
