from fastapi import APIRouter
from app.api.routes import user, auth, develop
from app.core.config import settings

router = APIRouter()


def include_api_routes():
    """Include routers"""
    router.include_router(auth.router, prefix=settings.API_V1_STR)
    router.include_router(user.router, prefix=settings.API_V1_STR)
    router.include_router(develop.router, prefix=settings.API_V1_STR)


include_api_routes()
