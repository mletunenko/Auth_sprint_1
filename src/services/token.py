import datetime

import backoff
from redis.asyncio import Redis
from redis.exceptions import ConnectionError


@backoff.on_exception(backoff.expo, ConnectionError, max_time=15)
async def invalidate_token(
        token: dict,
        redis: Redis,
) -> bool:
    jti = token["jti"]
    exp = token["exp"]
    return await redis.setex(f"blacklist:{jti}", exp - int(datetime.datetime.now().timestamp()), "true")

@backoff.on_exception(backoff.expo, ConnectionError, max_time=15)
async def check_invalid_token(
        token: dict,
        redis: Redis,
) -> bool:
    jti = token["jti"]
    res =  await redis.get(f"blacklist:{jti}")
    return res

