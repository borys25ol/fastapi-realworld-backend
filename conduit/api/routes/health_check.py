from fastapi import APIRouter

from version import response

router = APIRouter()


@router.get("/health-check")
async def health_check() -> dict:
    return response
