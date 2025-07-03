from fastapi import APIRouter, Depends, HTTPException, status
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.settings.caching import cache
from cachetools_async import cached
from app.settings.db import get_db
from app.user.schema import UserRequest


router = APIRouter()

@router.post("/api/user", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserRequest, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = dict(user.model_dump())
    try:
        result = await db.users.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(409, "User already exists")
    doc["_id"] = str(result.inserted_id)
    return doc

@router.get("/api/user/{id}")
@cached(cache)
async def get_user(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    doc = await db.users.find_one({"id":id})
    if doc is None:
        raise HTTPException(status_code=404, detail="User not found")
    doc["_id"] = str(doc["_id"])
    return doc
