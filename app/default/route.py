from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import time
import os
from app.settings.ratelimiter import rate_limiter
from app.settings.db import get_db
from motor.motor_asyncio import AsyncIOMotorDatabase


router = APIRouter()
router.mount("/static", StaticFiles(directory="app/static"), name="static")


@router.get("/health", dependencies=[Depends(rate_limiter)])
async def get_health():
    return {"health": "Ok"}

@router.get("/status")
async def get_status():
    index_file_path = os.path.join("app/static", "status.html")
    return FileResponse(index_file_path)

@router.get("/ready")
async def ready(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Readiness probe: returns 200 if MongoDB responds to 'ping'.
    Used by load balancers / Kubernetes.
    """
    try:
        await db.command("ping")
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

async def slow_job(tag: str):
    await asyncio.sleep(5)
    print(f"[{tag}] finished at", time.time())

@router.get("/api/test")
async def background_tasks(background: BackgroundTasks):
    start = time.time()
    background.add_task(slow_job, "Background Task 1")
    return {"message":"This is background task"}

