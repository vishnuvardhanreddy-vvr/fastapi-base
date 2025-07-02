import os
from app.settings.logging import logger
from typing import Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self)->None:

        self.APP_NAME = self._get("APP_NAME", default="fastAPI App")
        self.APP_VERSION = self._get("APP_VERSION", default="0.0.1")

        self.RATE_LIMIT_REQUESTS_COUNT = self._get("RATE_LIMIT_REQUESTS_COUNT", default=40)
        self.RATE_LIMIT_REQUESTS_TIME_IN_SECONDS = self._get("RATE_LIMIT_REQUESTS_TIME_IN_SECONDS", default=60)
        self.RATE_LIMIT_REQUESTS_STORAGE_TYPE = self._get("RATE_LIMIT_REQUESTS_STORAGE_TYPE", default="memory")
        self.REDIS_URL = self._get("REDIS_URL", default="")

        self.CACHING_LIMIT = self._get("CACHING_LIMIT", default=1024)
        self.CACHING_EXPIRY_TIME_IN_SECONDS = self._get("CACHING_EXPIRY_TIME_IN_SECONDS", default=60)
        self.CACHING_STORAGE_TYPE = self._get("CACHING_STORAGE_TYPE", default="memory")

        self.NEW_RELIC_APP_NAME = self._get("NEW_RELIC_APP_NAME", default=self.APP_NAME)
        self.NEW_RELIC_LICENSE_KEY = self._get("NEW_RELIC_LICENSE_KEY")


        self.MONGODB_MIN_POOL_SIZE = self._get("MONGODB_MIN_POOL_SIZE", default=1)
        self.MONGODB_MAX_POOL_SIZE = self._get("MONGODB_MAX_POOL_SIZE", default=2)
        self.MONGODB_CONNECTION_STRING = self._get("MONGODB_CONNECTION_STRING")
        self.MONGODB_CONNECTION_TIMEOUT_MS = self._get("MONGODB_CONNECTION_TIMEOUT_MS", default=30000)
        self.MONGODB_NAME = self._get("MONGODB_NAME")

        self.public_key = self._get("public-key", default="")
        self.public_endpoints = self._get("public_endpoints", default="/,/docs,/health,/status")
        self.ENVIRONMENT = self._get("ENVIRONMENT", default="local")
        self.ROLES = self._get("ROLES")



    def _get(self, key:str, default:Any|None = None):
        value = os.getenv(key)
        if value is None:
            if default is not None:
                logger.warning("[Config] Environment Variable '%s' not set, using default: '%s'", key, default)
                return default
            raise EnvironmentError(f"Missing required Environment Variable: '{key}'")
        return value
    
from functools import lru_cache

@lru_cache(maxsize=1)
def get_config():
    return Config()