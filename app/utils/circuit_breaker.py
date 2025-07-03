# app/utils/circuit_breaker.py
"""
Production‑ready async Circuit Breaker (zero external deps).

Usage
-----
from app.utils.circuit_breaker import cb, CircuitBreakerError

# decorator
@cb("email-service")
async def send_email(...):
    ...

# inline
try:
    data = await cb("user-api").call(fetch_user, user_id)
except CircuitBreakerError:
    ...  # fallback / 503

Env Vars
--------
CB_FAIL_MAX       : max consecutive failures before opening (default 5)
CB_RESET_TIMEOUT  : seconds breaker stays OPEN (default 30)
CB_NAME_PREFIX    : prefix in logs (default "cb")
"""

import asyncio
import logging
import os
import time
from enum import Enum, auto
from functools import wraps
from typing import Awaitable, Callable, Any, Dict
from app.settings.config import config

# ─────────────────── configuration ─────────────────────────────────────────

_FAIL_MAX      = int(config.CIRCUIT_BREAKER_FAIL_MAX_COUNT)
_RESET_TIMEOUT = int(config.CIRCUIT_BREAKER_RESET_TIMEOUT)
_PREFIX        = config.CIRCUIT_BREAKER_PREFIX_NAME

# ─────────────────── states ────────────────────────────────────────────────
class CircuitBreakerState(Enum):
    CLOSED = auto()
    OPEN = auto()
    HALF_OPEN = auto()

class CircuitBreakerError(RuntimeError):
    """Raised when the circuit is OPEN."""

# ─────────────────── core breaker class ────────────────────────────────────
class CircuitBreaker:
    def __init__(self, name: str, fail_max: int, reset_timeout: int):
        self.name = name
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self._state = CircuitBreakerState.CLOSED
        self._fail_counter = 0
        self._opened_at = 0.0
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------ api
    def __call__(self, fn: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        """Decorator usage."""
        if not asyncio.iscoroutinefunction(fn):
            raise TypeError("CircuitBreaker supports async callables only")

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            return await self.call(fn, *args, **kwargs)

        return wrapper

    async def call(self, fn: Callable[..., Awaitable[Any]], *args, **kwargs):
        """Inline wrapper usage: await breaker.call(coro, *args)."""
        await self._pre_execute()
        try:
            result = await fn(*args, **kwargs)
        except Exception:
            await self._record_failure()
            raise
        await self._record_success()
        return result

    # ---------------------------------------------------------------- state
    async def _pre_execute(self):
        async with self._lock:
            if self._state is CircuitBreakerState.OPEN:
                if (time.time() - self._opened_at) >= self.reset_timeout:
                    # move to HALF‑OPEN for trial
                    self._state = CircuitBreakerState.HALF_OPEN
                    logging.warning("[%s] OPEN → HALF_OPEN", self.name)
                else:
                    raise CircuitBreakerError(f"Circuit {self.name} is OPEN")
            # else CLOSED or HALF_OPEN: allow execution

    async def _record_failure(self):
        async with self._lock:
            self._fail_counter += 1
            if self._fail_counter >= self.fail_max:
                self._state = CircuitBreakerState.OPEN
                self._opened_at = time.time()
                logging.error("[%s] CLOSED/HALF_OPEN → OPEN (failures=%s)",
                              self.name, self._fail_counter)

    async def _record_success(self):
        async with self._lock:
            if self._state in (CircuitBreakerState.HALF_OPEN, CircuitBreakerState.OPEN):
                logging.info("[%s] %s → CLOSED", self.name, self._state.name)
            self._state = CircuitBreakerState.CLOSED
            self._fail_counter = 0

    # expose for introspection
    @property
    def current_state(self) -> CircuitBreakerState:
        return self._state

# ─────────────────── factory/cache ─────────────────────────────────────────
_breakers: Dict[str, CircuitBreaker] = {}

def _make(name: str) -> CircuitBreaker:
    full = f"{_PREFIX}:{name}"
    return CircuitBreaker(full, _FAIL_MAX, _RESET_TIMEOUT)

def cb(name: str) -> CircuitBreaker:
    """Get a named circuit breaker (creates once, re‑uses thereafter)."""
    if name not in _breakers:
        _breakers[name] = _make(name)
    return _breakers[name]
