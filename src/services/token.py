import datetime

import backoff
from redis.exceptions import ConnectionError
from redis.asyncio import Redis


@backoff.on_exception(backoff.expo, ConnectionError, max_time=15)
async def invalidate_token(
        token: dict,
        redis: Redis,
) -> bool:
    jti = token["jti"]
    exp = token["exp"]
    return await redis.setex(f"blacklist:{jti}", exp - int(datetime.datetime.now().timestamp()), "true")
