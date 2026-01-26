from fastapi import APIRouter

from conduit.api.schemas.responses.tag import TagsResponse
from conduit.core.dependencies import ITagService, UnitOfWork

router = APIRouter()


@router.get("", response_model=TagsResponse)
async def get_all_tags(uow: UnitOfWork, tag_service: ITagService) -> TagsResponse:
    """
    Return available all tags.
    """
    tags = await tag_service.get_all_tags(uow=uow)
    return TagsResponse.from_dtos(dtos=tags)
