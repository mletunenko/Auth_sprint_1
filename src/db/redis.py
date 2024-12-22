from typing import Optional
from redis import RedisError
from redis.asyncio import Redis

redis_client: Optional["Redis"] = None


async def get_redis_connection() -> Redis:
    try:
        return redis_client
    except RedisError as e:
        print(f"Ошибка подключения к Redis: {e}")
        raise
