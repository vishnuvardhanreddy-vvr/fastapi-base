import random, asyncio
from fastapi import APIRouter, HTTPException
from app.utils.circuit_breaker import cb, CircuitBreakerError
from app.utils.cb_utils import force_open, force_close, state

router = APIRouter(prefix="/cb")
demo_cb = cb("demo")

async def flaky():
    await asyncio.sleep(0.1)
    if True:
        raise RuntimeError("upstream failure")
    return {"data": "OK"}

@router.get("/call")
async def call():
    try:
        return await demo_cb.call(flaky)
    except CircuitBreakerError:
        raise HTTPException(503, f"Circuit breaker {demo_cb.current_state.name}! Service is down now.")

@router.get("/state")
async def get_state():
    return {"state": demo_cb.current_state.name}

@router.post("/open")
async def open_it():
    force_open("demo")
    return {"state": demo_cb.current_state.name}

@router.post("/close")
async def close_it():
    force_close("demo")
    return {"state": demo_cb.current_state.name}
