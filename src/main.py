from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import JSONResponse
from async_fastapi_jwt_auth.exceptions import AuthJWTException

from api.auth import router as auth_router
from api.account import router as account_router
from core.config import settings
from db.postgres import pg_helper


combined_router = APIRouter()
combined_router.include_router(auth_router)
combined_router.include_router(account_router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    yield
    # shutdown
    await pg_helper.dispose()


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
