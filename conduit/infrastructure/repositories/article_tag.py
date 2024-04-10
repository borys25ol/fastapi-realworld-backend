from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.dtos.tag import TagDTO
from conduit.domain.mapper import IModelMapper
from conduit.domain.repositories.article_tag import IArticleTagRepository
from conduit.infrastructure.models import ArticleTag, Tag


class ArticleTagRepository(IArticleTagRepository):
    """Repository for Article Tag model."""

    def __init__(self, tag_mapper: IModelMapper[Tag, TagDTO]):
        self._tag_mapper = tag_mapper

    async def create(
        self, session: AsyncSession, article_id: int, tags: list[TagDTO]
    ) -> None:
        query = insert(ArticleTag).values(
            [
                {
                    "article_id": article_id,
                    "tag_id": tag.id,
                    "created_at": datetime.now(),
                }
                for tag in tags
            ]
        )
        await session.execute(query)

    async def get_by_article_id(
        self, session: AsyncSession, article_id: int
    ) -> list[TagDTO]:
        query = select(Tag, ArticleTag).where(
            (ArticleTag.article_id == article_id) & (ArticleTag.tag_id == Tag.id)
        )
        tags = await session.scalars(query)
        return [self._tag_mapper.to_dto(tag) for tag in tags]
