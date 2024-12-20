import os

from dotenv import load_dotenv
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class BaseTestSettings(BaseSettings):
    # Если в окружении уже есть переменные, нужно их переписать
    def __init__(self, **data):
        env_file_path = data.pop('env_file_path', '.env.tests-local')

        if os.path.exists(env_file_path):
            load_dotenv(env_file_path, override=True)

        super().__init__(**data)


class RedisTestSettings(BaseTestSettings):
    redis_host: str = '127.0.0.1'
    redis_port: int = 6379


class WebAppTestSettings(BaseTestSettings):
    service_host: str = Field('127.0.0.1', validation_alias='FASTAPI_HOST')
    service_port: int = 8000

    @property
    def service_url(self) -> HttpUrl:
        return f'http://{self.service_host}:{self.service_port}'


redis_test_settings = RedisTestSettings(env_file_path='.env.tests-local')
webapp_test_settings = WebAppTestSettings(env_file_path='.env.tests-local')
