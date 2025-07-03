# app/utils/cb_admin.py
"""
Admin / test helpers for the circuit breaker.
Importing this does NOT mutate core logic.
"""

import time
import logging
from app.utils.circuit_breaker import cb, CircuitBreakerState

def force_open(name: str) -> None:
    brk = cb(name)
    brk._state = CircuitBreakerState.OPEN          # type: ignore
    brk._opened_at = time.time()
    logging.warning("[CircuitBreaker] %s forced → OPEN", brk.name)

def force_close(name: str) -> None:
    brk = cb(name)
    brk._state = CircuitBreakerState.CLOSED        # type: ignore
    brk._fail_counter = 0
    logging.warning("[CircuitBreaker] %s forced → CLOSED", brk.name)

def state(name: str) -> str:
    return cb(name).current_state.name
