from app.settings.db import get_db

db = get_db()

async def migrations():
    await db.users.create_index("id", unique=True)
