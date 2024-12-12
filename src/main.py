from contextlib import asynccontextmanager
from sys import prefix

import uvicorn
from fastapi import FastAPI

from api.auth import router as auth_router
from core.config import settings
from db.postgres import pg_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown
    await pg_helper.dispose()


app = FastAPI(
    lifespan=lifespan,
)
app.include_router(
    auth_router,
    prefix="/auth"
)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
