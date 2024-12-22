from typing import AsyncGenerator

from async_fastapi_jwt_auth import AuthJWT
from fastapi import HTTPException, status
from fastapi.params import Depends

from db.postgres import pg_helper
from db.repository import AsyncBaseRepository, AsyncSqlAlchemyRepository
from schemas.enums import SystemRoles


async def get_sqlalchemy_repository() -> AsyncGenerator[AsyncBaseRepository, None]:
    async with pg_helper.session_factory() as session:
        yield AsyncSqlAlchemyRepository(session)


async def check_superuser(authjwt: AuthJWT = Depends()):
    try:
        token = await authjwt.get_raw_jwt()
        user_role = token.get("roles")

        if user_role is not SystemRoles.SUPERUSER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden: Superuser required"
            )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token"
        )
