from app.settings.config import get_config
from cachetools import TTLCache
from redis.asyncio import from_url
from app.utils.redis_cache import AsyncRedisTTLCache

config = get_config()

if config.CACHING_STORAGE_TYPE == "redis":
    redis = from_url(config.REDIS_URL, encoding="utf8", decode_responses=True)
    cache = AsyncRedisTTLCache(redis, ttl=int(config.CACHING_EXPIRY_TIME_IN_SECONDS))
else:
    cache = TTLCache(
        maxsize=int(config.CACHING_LIMIT),
        ttl=int(config.CACHING_EXPIRY_TIME_IN_SECONDS),
    )
