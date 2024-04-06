from fastapi import APIRouter

from version import response

router = APIRouter()


@router.get("")
async def health_check() -> dict:
    return response
