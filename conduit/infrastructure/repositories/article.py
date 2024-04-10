from datetime import datetime

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from conduit.core.utils.slug import get_slug_from_title
from conduit.domain.dtos.article import ArticleDTO, CreateArticleDTO
from conduit.domain.mapper import IModelMapper
from conduit.domain.repositories.article import IArticleRepository
from conduit.infrastructure.models import Article


class ArticleRepository(IArticleRepository):

    def __init__(self, article_mapper: IModelMapper[Article, ArticleDTO]):
        self._article_mapper = article_mapper

    async def create(
        self, session: AsyncSession, author_id: int, create_item: CreateArticleDTO
    ) -> ArticleDTO:
        query = (
            insert(Article)
            .values(
                author_id=author_id,
                slug=get_slug_from_title(title=create_item.title),
                title=create_item.title,
                description=create_item.description,
                body=create_item.body,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            .returning(Article)
        )
        result = await session.execute(query)
        return self._article_mapper.to_dto(result.scalar())

    async def get_by_slug(self, session: AsyncSession, slug: str) -> ArticleDTO:
        query = select(Article).where(Article.slug == slug)
        result = await session.execute(query)
        return self._article_mapper.to_dto(result.scalar())

    async def get_by_author_ids(
        self, session: AsyncSession, author_ids: list[int]
    ) -> list[ArticleDTO]:
        query = select(Article).where(Article.author_id.in_(author_ids))
        articles = await session.scalars(query)
        return [self._article_mapper.to_dto(article) for article in articles]

    async def count_by_author_ids(
        self, session: AsyncSession, author_ids: list[int]
    ) -> int:
        query = select(count()).where(Article.author_id.in_(author_ids))
        result = await session.execute(query)
        return result.scalar()
