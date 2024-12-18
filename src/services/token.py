import datetime

import backoff
import redis


@backoff.on_exception(backoff.expo, ConnectionError, max_tries=15)
def invalidate_token(
        token: dict,
        redis: redis.Redis,
) -> bool:
    jti = token["jti"]
    exp = token["exp"]
    return redis.setex(f"blacklist:{jti}", exp - int(datetime.datetime.now().timestamp()), "true")
