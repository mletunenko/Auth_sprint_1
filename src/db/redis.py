import redis
from redis import RedisError

from core.config import settings

redis_client = redis.Redis(host=settings.redis.url, port=settings.redis.port)


async def get_redis_connection() -> redis.Redis:
    try:
        return redis_client
    except RedisError as e:
        print(f"Ошибка подключения к Redis: {e}")
        raise