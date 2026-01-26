from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.entities.tag import Tag as TagEntity
from conduit.domain.repositories.tag import ITagRepository
from conduit.infrastructure.mappers.tag_mapper import model_to_entity
from conduit.infrastructure.models import Tag


class TagRepository(ITagRepository):
    """Repository for Tag model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self) -> list[TagEntity]:
        query = select(Tag)
        tags = await self._session.scalars(query)
        return [model_to_entity(tag) for tag in tags]
