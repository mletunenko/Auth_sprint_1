from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from redis.asyncio import Redis
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

from api.account import router as account_router
from api.auth import router as auth_router
from api.role import router as role_router
from core.config import settings
from db import redis, postgres

combined_router = APIRouter()
combined_router.include_router(auth_router)
combined_router.include_router(account_router)
combined_router.include_router(role_router, prefix='/role')


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    redis.redis_client = Redis(
        host=settings.redis.url, port=settings.redis.port
    )
    postgres.pg_helper = postgres.PostgresHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )
    yield
    # shutdown
    await postgres.pg_helper.dispose()


app = FastAPI(
    lifespan=lifespan,
)
app.include_router(
    combined_router,
    prefix="/auth"
)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.message}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
