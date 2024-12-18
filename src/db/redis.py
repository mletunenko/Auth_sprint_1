from redis.asyncio import Redis
from redis import RedisError

from core.config import settings

redis_client = Redis(host=settings.redis.url, port=settings.redis.port)


async def get_redis_connection() -> Redis:
    try:
        return redis_client
    except RedisError as e:
        print(f"Ошибка подключения к Redis: {e}")
        raise