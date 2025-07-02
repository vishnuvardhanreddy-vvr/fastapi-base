import time
import asyncio
from abc import ABC, abstractmethod
from typing import Tuple
from fastapi import Request, HTTPException
from app.settings.config import get_config

config = get_config()

try:
    import redis.asyncio as aioredis   # redis‑py ≥ 4.2
except ImportError:
    aioredis = None  # Redis not installed – in‑memory fallback will be used



class BaseStorage(ABC):
    @abstractmethod
    async def incr(self, key: str, tokens: float, ttl: int) -> Tuple[float, bool]:
        """Increase token count by `tokens`. Return (new_count, is_new_bucket)."""
        pass


class MemoryStorage(BaseStorage):
    def __init__(self):
        self._buckets = {}
        self._lock = asyncio.Lock()

    async def incr(self, key, tokens, ttl):
        async with self._lock:
            now = time.time()
            count, expires = self._buckets.get(key, (0.0, 0))
            if now > expires:
                count = 0.0
                expires = now + ttl
            count += tokens
            self._buckets[key] = (count, expires)
            return count, now > expires


class RedisStorage(BaseStorage):
    LUA = """
    local new = redis.call('INCRBYFLOAT', KEYS[1], ARGV[1])
    if new == tonumber(ARGV[1]) then
        redis.call('EXPIRE', KEYS[1], ARGV[2])
    end
    return new
    """

    def __init__(self):
        redis_client = aioredis.from_url(get_config.REDIS_URL)
        self.redis = redis_client
        self.script = self.redis.register_script(self.LUA)

    async def incr(self, key, tokens, ttl):
        new_val = float(await self.script(keys=[key], args=[tokens, ttl]))
        return new_val, False


class RateLimiter:
    def __init__(
        self,
        limit: int,
        *,
        seconds: int = 0,
        storage: BaseStorage
    ):
        if seconds <= 0:
            raise ValueError("Must specify a positive time window using `seconds`.")

        self.capacity = limit
        self.refill_rate = limit / seconds
        self.storage = storage
        self.ttl = seconds

    async def allow(self, key: str) -> bool:
        current, _ = await self.storage.incr(key, 1, self.ttl)  # add just 1 hit
        return current <= self.capacity



def _build_storage(storage_type: str) -> BaseStorage:
    if storage_type == "redis":
        if aioredis is None:
            raise RuntimeError("Redis backend requested but redis-py is not installed.")
        return RedisStorage()
    return MemoryStorage()

limiter = RateLimiter(limit=int(config.RATE_LIMIT_REQUESTS_COUNT), seconds=int(config.RATE_LIMIT_REQUESTS_TIME_IN_SECONDS), storage=_build_storage(config.RATE_LIMIT_REQUESTS_STORAGE_TYPE))

async def check_rate(request: Request):
    client_ip = request.client.host
    if not await limiter.allow(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")