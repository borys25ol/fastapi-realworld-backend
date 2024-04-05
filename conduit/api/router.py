from fastapi import APIRouter

from conduit.api.routes import health_check, users

router = APIRouter()

router.include_router(router=health_check.router, tags=["Health Check"])
router.include_router(router=users.router, tags=["User and Authentication"])
