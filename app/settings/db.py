import atexit
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.settings.config import config

_config = config

_client: AsyncIOMotorClient = AsyncIOMotorClient(
    _config.MONGODB_CONNECTION_STRING,
    maxPoolSize=int(_config.MONGODB_MAX_POOL_SIZE),
    minPoolSize=int(_config.MONGODB_MIN_POOL_SIZE),
    serverSelectionTimeoutMS=int(_config.MONGODB_CONNECTION_TIMEOUT_MS)
)

# 2. close pool automatically when the process exits
atexit.register(_client.close)

# 3. FastAPI dependency
def get_db() -> AsyncIOMotorDatabase:
    """Return the database handle; Motor connects on first use."""
    return _client[_config.MONGODB_NAME]
