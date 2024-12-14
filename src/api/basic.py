from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from db.postgres import pg_helper

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.auth_jwt import AuthJWTBearer

from schemas.user import UserAccountLogin, LoginResponse
from services.account import get_current_user as service_get_current_user


router = APIRouter()
auth_dep = AuthJWTBearer()


# in production, you can use Settings management
# from pydantic to get secret key from .env
class Settings(BaseModel):
    authjwt_secret_key: str = "secret"      # TODO to get secret key from .env


# callback to get your configuration
@AuthJWT.load_config
def get_config():
    return Settings()


# provide a method to create access tokens. The create_access_token()
# function is used to actually generate the token to use authorization
# later in endpoint protected
@router.post("/login", response_model=LoginResponse)
async def login(
    user: UserAccountLogin,
    authorize: AuthJWT = Depends(auth_dep),
    session: AsyncSession = Depends(pg_helper.session_getter),
):
    user = await service_get_current_user(email=user.email, session=session)

    # subject identifier for whom this token is for example id or username from database
    access_token = await authorize.create_access_token(subject=str(user.id))
    return {"access_token": access_token}
