from datetime import datetime

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from conduit.core.utils.slug import get_slug_from_title
from conduit.domain.dtos.article import ArticleDTO, CreateArticleDTO, UpdateArticleDTO
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

    async def get_by_slug(self, session: AsyncSession, slug: str) -> ArticleDTO | None:
        query = select(Article).where(Article.slug == slug)
        if article := await session.scalar(query):
            return self._article_mapper.to_dto(article)

    async def delete_by_slug(self, session: AsyncSession, slug: str) -> None:
        query = delete(Article).where(Article.slug == slug)
        await session.execute(query)

    async def update_by_slug(
        self, session: AsyncSession, slug: str, update_item: UpdateArticleDTO
    ) -> ArticleDTO:
        query = (
            update(Article)
            .where(Article.slug == slug)
            .values(updated_at=datetime.now())
            .returning(Article)
        )
        if update_item.title is not None:
            query = query.values(
                title=update_item.title,
                slug=get_slug_from_title(title=update_item.title),
            )
        if update_item.description is not None:
            query = query.values(description=update_item.description)
        if update_item.body is not None:
            query = query.values(body=update_item.body)

        article = await session.scalar(query)
        return self._article_mapper.to_dto(article)

    async def get_by_author_ids(
        self, session: AsyncSession, author_ids: list[int]
    ) -> list[ArticleDTO]:
        query = select(Article).where(Article.author_id.in_(author_ids))
        articles = await session.scalars(query)
        return [self._article_mapper.to_dto(article) for article in articles]

    async def get_all(self, session: AsyncSession) -> list[ArticleDTO]:
        query = select(Article)
        articles = await session.scalars(query)
        return [self._article_mapper.to_dto(article) for article in articles]

    async def count_by_author_ids(
        self, session: AsyncSession, author_ids: list[int]
    ) -> int:
        query = select(count()).where(Article.author_id.in_(author_ids))
        result = await session.execute(query)
        return result.scalar()

    async def count_all(self, session: AsyncSession) -> int:
        query = select(count(Article.id))
        result = await session.execute(query)
        return result.scalar()
