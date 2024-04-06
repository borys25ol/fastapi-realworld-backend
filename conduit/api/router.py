from fastapi import APIRouter

from conduit.api.routes import authentication, health_check, users

router = APIRouter()

router.include_router(
    router=health_check.router, tags=["Health Check"], prefix="/health-check"
)
router.include_router(
    router=authentication.router, tags=["Authentication"], prefix="/users"
)
router.include_router(router=users.router, tags=["Users"], prefix="/user")
