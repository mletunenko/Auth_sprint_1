import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse, ORJSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            ConsoleSpanExporter)
from redis.asyncio import Redis
from starlette.middleware.cors import CORSMiddleware

from api.account import router as account_router
from api.auth import router as auth_router
from api.role import router as role_router
from core.config import settings
from db import postgres, redis

combined_router = APIRouter()
combined_router.include_router(auth_router)
combined_router.include_router(account_router)
combined_router.include_router(role_router, prefix="/role")


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

def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.jaeger.host,
                agent_port=settings.jaeger.agent_port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

configure_tracer()
app = FastAPI(
    lifespan=lifespan,
)

FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id",  str(uuid.uuid4()))
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    return response


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
