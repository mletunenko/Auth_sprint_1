import logging
from typing import Optional

from redis import RedisError
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

redis_client: Optional["Redis"] = None


async def get_redis_connection() -> Redis:
    try:
        return redis_client
    except RedisError as e:
        logger.error(f"Ошибка подключения к Redis: {e}")
        raise
