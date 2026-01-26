from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.entities.tag import Tag as TagEntity
from conduit.domain.repositories.article_tag import IArticleTagRepository
from conduit.infrastructure.models import ArticleTag, Tag


class ArticleTagRepository(IArticleTagRepository):
    """Repository for Article Tag model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_tag_entity(model: Tag) -> TagEntity:
        return TagEntity(id=model.id, tag=model.tag, created_at=model.created_at)

    async def add_many(self, article_id: int, tags: list[str]) -> list[TagEntity]:
        insert_query = (
            insert(Tag)
            .on_conflict_do_nothing()
            .values([dict(tag=tag, created_at=datetime.now()) for tag in tags])
        )
        await self._session.execute(insert_query)

        select_query = select(Tag).where(Tag.tag.in_(tags))
        selected_tags = await self._session.scalars(select_query)
        tag_records = [self._to_tag_entity(tag) for tag in selected_tags]

        link_query = (
            insert(ArticleTag)
            .on_conflict_do_nothing()
            .values(
                [
                    dict(
                        article_id=article_id,
                        tag_id=tag_record.id,
                        created_at=datetime.now(),
                    )
                    for tag_record in tag_records
                ]
            )
        )
        await self._session.execute(link_query)

        return tag_records

    async def list(self, article_id: int) -> list[TagEntity]:
        query = (
            select(Tag, ArticleTag)
            .where(
                (ArticleTag.article_id == article_id) & (ArticleTag.tag_id == Tag.id)
            )
            .order_by(Tag.created_at.desc())
        )
        tags = await self._session.scalars(query)
        return [self._to_tag_entity(tag) for tag in tags]
