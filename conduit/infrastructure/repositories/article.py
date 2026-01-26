from datetime import datetime
from typing import Any

from sqlalchemy import delete, exists, func, insert, select, true, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import count

from conduit.application.queries.article_feed import ArticleFeedRecordDTO
from conduit.core.exceptions import ArticleNotFoundException
from conduit.core.utils.slug import get_slug_unique_part
from conduit.domain.entities.article import Article as ArticleEntity
from conduit.domain.repositories.article import IArticleRepository
from conduit.infrastructure.mappers.article_mapper import model_to_entity
from conduit.infrastructure.models import (
    Article,
    ArticleTag,
    Favorite,
    Follower,
    Tag,
    User,
)

# Aliases for the models if needed.
FavoriteAlias = aliased(Favorite)


class ArticleRepository(IArticleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_article_feed_record_dto(res: Any) -> ArticleFeedRecordDTO:
        tags = res.tags.split(", ") if res.tags else []
        return ArticleFeedRecordDTO(
            id=res.id,
            author_id=res.author_id,
            slug=res.slug,
            title=res.title,
            description=res.description,
            body=res.body,
            tags=tags,
            author_username=res.username,
            author_bio=res.bio,
            author_image_url=res.image_url,
            author_following=res.following,
            created_at=res.created_at,
            updated_at=res.updated_at,
            favorited=res.favorited,
            favorites_count=res.favorites_count,
        )

    async def add(self, article: ArticleEntity) -> ArticleEntity:
        query = (
            insert(Article)
            .values(
                author_id=article.author_id,
                slug=article.slug,
                title=article.title,
                description=article.description,
                body=article.body,
                created_at=article.created_at,
                updated_at=article.updated_at or article.created_at,
            )
            .returning(Article)
        )
        result = await self._session.execute(query)
        return model_to_entity(result.scalar_one())

    async def get_by_slug_or_none(self, slug: str) -> ArticleEntity | None:
        slug_unique_part = get_slug_unique_part(slug=slug)
        query = select(Article).where(
            Article.slug == slug or Article.slug.contains(slug_unique_part)
        )
        if article := await self._session.scalar(query):
            return model_to_entity(article)

    async def get_by_slug(self, slug: str) -> ArticleEntity:
        slug_unique_part = get_slug_unique_part(slug=slug)
        query = select(Article).where(
            Article.slug == slug or Article.slug.contains(slug_unique_part)
        )
        if not (article := await self._session.scalar(query)):
            raise ArticleNotFoundException()
        return model_to_entity(article)

    async def delete_by_slug(self, slug: str) -> None:
        query = delete(Article).where(Article.slug == slug)
        await self._session.execute(query)

    async def update_by_slug(self, slug: str, article: ArticleEntity) -> ArticleEntity:
        query = (
            update(Article)
            .where(Article.slug == slug)
            .values(updated_at=article.updated_at or datetime.now())
            .returning(Article)
        )
        query = query.values(
            title=article.title,
            slug=article.slug,
            description=article.description,
            body=article.body,
        )

        article_model = await self._session.scalar(query)
        if article_model is None:
            raise ArticleNotFoundException()
        return model_to_entity(article_model)

    async def list_by_followings(
        self, user_id: int, limit: int, offset: int
    ) -> list[ArticleFeedRecordDTO]:
        query = (
            select(
                Article.id.label("id"),
                Article.author_id.label("author_id"),
                Article.slug.label("slug"),
                Article.title.label("title"),
                Article.description.label("description"),
                Article.body.label("body"),
                Article.created_at.label("created_at"),
                Article.updated_at.label("updated_at"),
                User.username.label("username"),
                User.bio.label("bio"),
                User.image_url.label("image_url"),
                true().label("following"),
                # Subquery for favorites count.
                select(func.count(Favorite.article_id))
                .where(Favorite.article_id == Article.id)
                .scalar_subquery()
                .label("favorites_count"),
                # Subquery to check if favorited by user with id `user_id`.
                exists()
                .where(
                    (Favorite.user_id == user_id) & (Favorite.article_id == Article.id)
                )
                .label("favorited"),
                # Concatenate tags.
                func.string_agg(Tag.tag, ", ").label("tags"),
            )
            .join(User, Article.author_id == User.id)
            .join(ArticleTag, Article.id == ArticleTag.article_id, isouter=True)
            .join(Tag, Tag.id == ArticleTag.tag_id, isouter=True)
            .filter(
                User.id.in_(
                    select(Follower.following_id)
                    .where(Follower.follower_id == user_id)
                    .scalar_subquery()
                )
            )
            .group_by(
                Article.id,
                Article.author_id,
                Article.slug,
                Article.title,
                Article.description,
                Article.body,
                Article.created_at,
                Article.updated_at,
                User.id,
                User.username,
                User.bio,
                User.email,
                User.image_url,
            )
        )
        query = query.limit(limit).offset(offset)
        articles = await self._session.execute(query)

        return [self._to_article_feed_record_dto(article) for article in articles]

    async def list_by_filters(
        self,
        user_id: int | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> list[ArticleFeedRecordDTO]:
        query = (
            # fmt: off
            select(
                Article.id.label("id"),
                Article.author_id.label("author_id"),
                Article.slug.label("slug"),
                Article.title.label("title"),
                Article.description.label("description"),
                Article.body.label("body"),
                Article.created_at.label("created_at"),
                Article.updated_at.label("updated_at"),
                User.username.label("username"),
                User.bio.label("bio"),
                User.image_url.label("image_url"),
                exists()
                .where(
                    (Follower.follower_id == user_id)
                    & (Follower.following_id == Article.author_id)
                )
                .label("following"),
                # Subquery for favorites count.
                select(func.count(Favorite.article_id))
                .where(Favorite.article_id == Article.id)
                .scalar_subquery()
                .label("favorites_count"),
                # Subquery to check if favorited by user with id `user_id`.
                exists()
                .where(
                    (Favorite.user_id == user_id) & (Favorite.article_id == Article.id)
                )
                .label("favorited"),
                # Concatenate tags.
                func.string_agg(Tag.tag, ", ").label("tags"),
            )
            .outerjoin(User, Article.author_id == User.id)
            .outerjoin(ArticleTag, Article.id == ArticleTag.article_id)
            .outerjoin(FavoriteAlias, FavoriteAlias.article_id == Article.id)
            .outerjoin(Tag, Tag.id == ArticleTag.tag_id)
            .group_by(
                Article.id,
                Article.author_id,
                Article.slug,
                Article.title,
                Article.description,
                Article.body,
                Article.created_at,
                Article.updated_at,
                User.id,
                User.username,
                User.bio,
                User.email,
                User.image_url,
            )
            # fmt: on
        )

        if author is not None:
            query = query.where(User.username == author)

        if tag is not None:
            query = query.where(Tag.tag == tag)

        if favorited is not None:
            favorited_user_id = (
                select(User.id).where(User.username == favorited).scalar_subquery()
            )
            query = query.where(FavoriteAlias.user_id == favorited_user_id)

        query = query.limit(limit).offset(offset)
        articles = await self._session.execute(query)
        return [self._to_article_feed_record_dto(article) for article in articles]

    async def count_by_followings(self, user_id: int) -> int:
        query = select(count(Article.id)).join(
            Follower,
            (
                (Follower.following_id == Article.author_id)
                & (Follower.follower_id == user_id)
            ),
        )
        result = await self._session.execute(query)
        return int(result.scalar_one())

    async def count_by_filters(
        self,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> int:
        query = select(count(Article.id))

        if tag:
            # fmt: off
            query = query.join(
                ArticleTag,
                (Article.id == ArticleTag.article_id),
            ).where(
                ArticleTag.tag_id == select(Tag.id).where(
                    Tag.tag == tag
                ).scalar_subquery()
            )
            # fmt: on

        if author:
            # fmt: off
            query = query.join(
                User,
                (User.id == Article.author_id)
            ).where(
                User.username == author
            )
            # fmt: on

        if favorited:
            # fmt: off
            query = query.join(
                Favorite,
                (Favorite.article_id == Article.id)
            ).where(
                Favorite.user_id == select(User.id).where(
                    User.username == favorited
                ).scalar_subquery()
            )
            # fmt: on

        result = await self._session.execute(query)
        return int(result.scalar_one())
