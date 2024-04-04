from fastapi import APIRouter

from conduit.api.routes import health_check

router = APIRouter()

router.include_router(router=health_check.router, tags=["Health Check"], prefix="")
