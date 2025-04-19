import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import APIRouter, Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from redis.asyncio import Redis

from api.account import router as account_router
from api.auth import router as auth_router
from api.users import router as users_router
from core.config import settings
from db import postgres, redis
from db.rabbit import RabbitMQConnection

combined_router = APIRouter()
combined_router.include_router(auth_router)
combined_router.include_router(account_router)
combined_router.include_router(users_router)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    redis.redis_client = Redis(host=settings.redis.url, port=settings.redis.port)
    postgres.pg_helper = postgres.PostgresHelper(
        url=str(settings.db.url),
        echo=settings.db.echo,
        echo_pool=settings.db.echo_pool,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
    )
    await FastAPILimiter.init(redis.redis_client)
    yield
    # shutdown
    await postgres.pg_helper.dispose()


def configure_tracer() -> None:
    provider = TracerProvider()
    trace.set_tracer_provider(provider)
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.jaeger.host,
        agent_port=settings.jaeger.agent_port,
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(span_processor)
    # Чтобы видеть трейсы в консоли
    # trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


if settings.enable_tracer:
    configure_tracer()

app = FastAPI(
    lifespan=lifespan,
    dependencies=[Depends(RateLimiter(times=settings.rate_limiter.times, seconds=settings.rate_limiter.seconds))],
)

FastAPIInstrumentor.instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "X-Request-Id is required"})
    return response


app.include_router(combined_router, prefix="/auth")


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


if __name__ == "__main__":
    rabbit = RabbitMQConnection()
    asyncio.run(rabbit.declare_queues())

    uvicorn.run(
        "web_server:app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
