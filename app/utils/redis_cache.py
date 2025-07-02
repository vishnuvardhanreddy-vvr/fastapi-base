from redis.asyncio import Redis
from typing import Any
import json

class AsyncRedisTTLCache:
    """
    Minimal TTL cache with the same async interface expected by
    cachetools_async.cached().
    Stores JSON-serialisable objects by default; you can swap to pickle.
    """
    def __init__(self, redis: Redis, ttl: int, prefix: str = "acache"):
        self.r = redis
        self.ttl = ttl
        self.prefix = prefix

    def _k(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Any:
        raw = await self.r.get(self._k(key))
        return None if raw is None else json.loads(raw)

    async def set(self, key: str, value: Any) -> None:
        await self.r.set(self._k(key), json.dumps(value), ex=self.ttl)
