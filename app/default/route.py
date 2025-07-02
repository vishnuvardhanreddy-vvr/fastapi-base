from fastapi import APIRouter, Depends, BackgroundTasks
import asyncio
import time
from app.settings.ratelimiter import check_rate


router = APIRouter()

@router.get("/health", dependencies=[Depends(check_rate)])
async def get_health():
    return {"health": "Ok"}

@router.get("/status")
async def get_status():
    return {"status": "Ok"}

async def slow_job(tag: str):
    await asyncio.sleep(5)
    print(f"[{tag}] finished at", time.time())

@router.get("/api/test")
async def background_tasks(background: BackgroundTasks):
    start = time.time()
    background.add_task(slow_job, "Background Task 1")
    return {"message":"This is background task"}

