from fastapi import APIRouter

from conduit.api.routes import authentication, health_check, profile, tag, users

router = APIRouter()

router.include_router(
    router=health_check.router, tags=["Health Check"], prefix="/health-check"
)
router.include_router(
    router=authentication.router, tags=["Authentication"], prefix="/users"
)
router.include_router(router=users.router, tags=["User"], prefix="/user")
router.include_router(router=profile.router, tags=["Profiles"], prefix="/profiles")
router.include_router(router=tag.router, tags=["Tags"], prefix="/tags")
