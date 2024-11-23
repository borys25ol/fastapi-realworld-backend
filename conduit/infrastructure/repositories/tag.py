from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.dtos.tag import TagDTO
from conduit.domain.mapper import IModelMapper
from conduit.domain.repositories.tag import ITagRepository
from conduit.infrastructure.models import Tag


class TagRepository(ITagRepository):
    """Repository for Tag model."""

    def __init__(self, tag_mapper: IModelMapper[Tag, TagDTO]):
        self._tag_mapper = tag_mapper

    async def list(self, session: AsyncSession) -> list[TagDTO]:
        query = select(Tag)
        tags = await session.scalars(query)
        return [self._tag_mapper.to_dto(tag) for tag in tags]
