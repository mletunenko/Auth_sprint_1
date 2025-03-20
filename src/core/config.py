from logging import config as logging_config
from pathlib import Path

from async_fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

BASE_DIR = Path(__file__).parent.parent

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class DatabaseConfig(BaseModel):
    url: PostgresDsn = "postgresql+asyncpg://user:password@127.0.0.1:30001/auth"
    sync_url: PostgresDsn = "postgresql+psycopg://user:password@auth_postgres:30001/auth"
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10

    naming_conventions: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class RedisConfig(BaseModel):
    url: str = "localhost"
    port: int = 6379


class YandexAuth(BaseModel):
    client_id: str = "bb42c906391e4aa6ab53d4ac7359b8a4"
    client_secret: str = "f297dc281fe44371bf812f3df0326dae"
    redirect_uri: str = "http://127.0.0.1:8000/auth/yandex_id_login/primary_redirect"
    oauth_url: str = "https://oauth.yandex.ru/authorize"
    token_url: str = "https://oauth.yandex.ru/token"
    user_info_url: str = "https://login.yandex.ru/info"


class JaegerConfig(BaseModel):
    host: str = "127.0.0.1"
    agent_port: int = 6831


class RateLimiter(BaseModel):
    seconds: int = 2
    times: int = 20


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".dev.env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    db: DatabaseConfig = DatabaseConfig()
    authjwt_secret_key: str = "secret"
    algorithm: str = "HS256"
    redis: RedisConfig = RedisConfig()
    yandex_auth: YandexAuth = YandexAuth()
    enable_tracer: bool = True
    jaeger: JaegerConfig = JaegerConfig()
    rate_limiter: RateLimiter = RateLimiter()


settings = Settings()


@AuthJWT.load_config
def get_config():
    return settings
