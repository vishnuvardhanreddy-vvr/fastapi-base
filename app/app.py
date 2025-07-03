from fastapi import FastAPI
from app.default.route import router as DefaultRouter
from app.user.route import router as UserRouter
from app.admin_test.route import router as CbRouter
from app.settings.monitor import Monitor
from app.settings.config import config
from app.middlewares.auth import TokenMiddleware

monitor = Monitor()

app = FastAPI(title=config.APP_NAME, version=config.APP_VERSION, description="Base FastAPI app")

app.add_middleware(TokenMiddleware)


app.include_router(router=DefaultRouter, tags=["default"])
app.include_router(router=UserRouter, tags=["user"])

app.include_router(router=CbRouter, tags=["Test Routes"])
