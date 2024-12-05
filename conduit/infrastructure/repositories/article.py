from datetime import datetime
from typing import Any

from sqlalchemy import case, delete, exists, func, insert, select, true, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import count

from conduit.core.exceptions import ArticleNotFoundException
from conduit.core.utils.slug import (
    get_slug_unique_part,
    make_slug_from_title,
    make_slug_from_title_and_code,
)
from conduit.domain.dtos.article import (
    ArticleAuthorDTO,
    ArticleDTO,
    ArticleRecordDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
    ArticleVersionDTO,
)
from conduit.domain.mapper import IModelMapper
from conduit.domain.repositories.article import IArticleRepository
from conduit.infrastructure.models import (
    Article,
    ArticleTag,
    Favorite,
    Follower,
    Tag,
    User,
    ArticleVersion,
)

# Aliases for the models if needed.
FavoriteAlias = aliased(Favorite)


class ArticleRepository(IArticleRepository):

    def __init__(self, article_mapper: IModelMapper[Article, ArticleRecordDTO]):
        self._article_mapper = article_mapper

    async def add(
        self, session: AsyncSession, author_id: int, create_item: CreateArticleDTO
    ) -> ArticleRecordDTO:
        query = (
            insert(Article)
            .values(
                author_id=author_id,
                slug=make_slug_from_title(title=create_item.title),
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

    async def get_by_slug_or_none(
        self, session: AsyncSession, slug: str
    ) -> ArticleRecordDTO | None:
        slug_unique_part = get_slug_unique_part(slug=slug)
        query = select(Article).where(
            Article.slug == slug or Article.slug.contains(slug_unique_part)
        )
        if article := await session.scalar(query):
            return self._article_mapper.to_dto(article)

    async def get_by_slug(self, session: AsyncSession, slug: str) -> ArticleRecordDTO:
        slug_unique_part = get_slug_unique_part(slug=slug)
        query = select(Article).where(
            Article.slug == slug or Article.slug.contains(slug_unique_part)
        )
        if not (article := await session.scalar(query)):
            raise ArticleNotFoundException()
        return self._article_mapper.to_dto(article)

    async def delete_by_slug(self, session: AsyncSession, slug: str) -> None:
        query = delete(Article).where(Article.slug == slug)
        await session.execute(query)

    async def update_by_slug(
        self, session: AsyncSession, slug: str, update_item: UpdateArticleDTO
    ) -> ArticleRecordDTO:
        query = (
            update(Article)
            .where(Article.slug == slug)
            .values(updated_at=datetime.now())
            .returning(Article)
        )
        if update_item.title is not None:
            updated_slug = make_slug_from_title_and_code(
                title=update_item.title, code=get_slug_unique_part(slug=slug)
            )
            query = query.values(title=update_item.title, slug=updated_slug)
        if update_item.description is not None:
            query = query.values(description=update_item.description)
        if update_item.body is not None:
            query = query.values(body=update_item.body)

        article = await session.scalar(query)
        return self._article_mapper.to_dto(article)

    async def list_by_followings(
        self, session: AsyncSession, user_id: int, limit: int, offset: int
    ) -> list[ArticleRecordDTO]:
        query = (
            (
                select(
                    Article.id,
                    Article.author_id,
                    Article.slug,
                    Article.title,
                    Article.description,
                    Article.body,
                    Article.created_at,
                    Article.updated_at,
                    User.username,
                    User.bio,
                    User.image_url,
                )
            )
            .join(
                Follower,
                (
                    (Follower.following_id == Article.author_id)
                    & (Follower.follower_id == user_id)
                ),
            )
            .join(User, (User.id == Article.author_id))
            .order_by(Article.created_at)
        )
        query = query.limit(limit).offset(offset)
        articles = await session.execute(query)
        return [self._article_mapper.to_dto(article) for article in articles]

    async def list_by_followings_v2(
        self, session: AsyncSession, user_id: int, limit: int, offset: int
    ) -> list[ArticleDTO]:
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
                User.id.label("user_id"),
                User.username.label("username"),
                User.bio.label("bio"),
                User.email.label("email"),
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
            .join(ArticleTag, Article.id == ArticleTag.article_id)
            .join(Tag, Tag.id == ArticleTag.tag_id)
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
        articles = await session.execute(query)

        return [self._to_article_dto(article) for article in articles]

    async def list_by_filters(
        self,
        session: AsyncSession,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> list[ArticleRecordDTO]:
        query = (
            select(
                Article.id,
                Article.author_id,
                Article.slug,
                Article.title,
                Article.description,
                Article.body,
                Article.created_at,
                Article.updated_at,
            )
        ).order_by(Article.created_at)

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

        query = query.limit(limit).offset(offset)
        articles = await session.execute(query)
        return [self._article_mapper.to_dto(article) for article in articles]

    async def list_by_filters_v2(
        self,
        session: AsyncSession,
        user_id: int | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> list[ArticleDTO]:
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
                User.id.label("user_id"),
                User.username.label("username"),
                User.bio.label("bio"),
                User.email.label("email"),
                User.image_url.label("image_url"),
                exists()
                .where(
                    (Follower.follower_id == user_id) &
                    (Follower.following_id == Article.author_id)
                )
                .label("following"),
                # Subquery for favorites count.
                select(
                    func.count(Favorite.article_id)
                ).where(
                    Favorite.article_id == Article.id).scalar_subquery()
                .label("favorites_count"),
                # Subquery to check if favorited by user with id `user_id`.
                exists()
                .where(
                    (Favorite.user_id == user_id) &
                    (Favorite.article_id == Article.id)
                )
                .label("favorited"),
                # Concatenate tags.
                func.string_agg(Tag.tag, ", ").label("tags"),
            )
            .outerjoin(User, Article.author_id == User.id)
            .outerjoin(ArticleTag, Article.id == ArticleTag.article_id)
            .outerjoin(FavoriteAlias, FavoriteAlias.article_id == Article.id)
            .outerjoin(Tag, Tag.id == ArticleTag.tag_id)
            .filter(
                Article.is_draft == False,
                # Filter by author username if provided.
                case((author is not None, User.username == author), else_=True),
                # Filter by tag if provided.
                case((tag is not None, Tag.tag == tag), else_=True),
                # Filter by "favorited by" username if provided.
                case(
                    (
                        favorited is not None,
                        FavoriteAlias.user_id == select(User.id)
                        .where(User.username == favorited)
                        .scalar_subquery(),
                    ),
                    else_=True,
                ),
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
        articles = await session.execute(query)
        return [self._to_article_dto(article) for article in articles]

    async def count_by_followings(self, session: AsyncSession, user_id: int) -> int:
        query = select(count(Article.id)).join(
            Follower,
            (
                (Follower.following_id == Article.author_id)
                & (Follower.follower_id == user_id)
            ),
        )
        result = await session.execute(query)
        return result.scalar()

    async def count_by_filters(
        self,
        session: AsyncSession,
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

        result = await session.execute(query)
        return result.scalar()

    async def add_draft(
        self, session: AsyncSession, author_id: int, create_item: CreateArticleDTO
    ) -> ArticleRecordDTO:
        now = datetime.now()
        slug = make_slug_from_title(create_item.title)
        
        # Insert the article
        article_query = (
            insert(Article)
            .values(
                author_id=author_id,
                slug=slug,
                title=create_item.title,
                description=create_item.description,
                body=create_item.body,
                created_at=now,
                updated_at=now,
                is_draft=True,
                current_version=1,
            )
            .returning(Article)
        )
        result = await session.execute(article_query)
        article = result.scalar_one()
        
        # Create initial version
        version_query = insert(ArticleVersion).values(
            article_id=article.id,
            version=1,
            title=create_item.title,
            description=create_item.description,
            body=create_item.body,
            created_at=now,
        )
        await session.execute(version_query)
        
        return ArticleRecordDTO(
            id=article.id,
            author_id=article.author_id,
            slug=article.slug,
            title=article.title,
            description=article.description,
            body=article.body,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    async def publish_draft(
        self, session: AsyncSession, slug: str, author_id: int
    ) -> ArticleRecordDTO:
        query = (
            update(Article)
            .where(Article.slug == slug, Article.author_id == author_id)
            .values(is_draft=False, updated_at=datetime.now())
            .returning(Article)
        )
        result = await session.execute(query)
        article = result.scalar_one_or_none()
        if not article:
            raise ArticleNotFoundException()
        
        return ArticleRecordDTO(
            id=article.id,
            author_id=article.author_id,
            slug=article.slug,
            title=article.title,
            description=article.description,
            body=article.body,
            created_at=article.created_at,
            updated_at=article.updated_at,
        )

    async def get_versions(
        self, session: AsyncSession, slug: str, author_id: int
    ) -> list[ArticleVersionDTO]:
        query = (
            select(ArticleVersion)
            .join(Article)
            .where(
                Article.slug == slug,
                Article.author_id == author_id
            )
            .order_by(ArticleVersion.version.desc())
        )
        result = await session.execute(query)
        versions = result.scalars().all()
        
        return [
            ArticleVersionDTO(
                id=version.id,
                article_id=version.article_id,
                version=version.version,
                title=version.title,
                description=version.description,
                body=version.body,
                created_at=version.created_at,
            )
            for version in versions
        ]

    async def list_drafts(
        self, session: AsyncSession, author_id: int, limit: int, offset: int
    ) -> list[ArticleDTO]:
        query = (
            select(Article)
            .where(
                Article.author_id == author_id,
                Article.is_draft == True
            )
            .order_by(Article.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await session.execute(query)
        articles = result.scalars().all()
        
        return await self._get_articles_with_relations(
            session=session,
            articles=articles,
            user_id=author_id
        )

    @staticmethod
    def _to_article_dto(res: Any) -> ArticleDTO:
        return ArticleDTO(
            id=res.id,
            author_id=res.author_id,
            slug=res.slug,
            title=res.title,
            description=res.description,
            body=res.body,
            tags=res.tags,
            author=ArticleAuthorDTO(
                username=res.username,
                bio=res.bio,
                image=res.image_url,
                following=res.following,
            ),
            created_at=res.created_at,
            updated_at=res.updated_at,
            favorited=res.favorited,
            favorites_count=res.favorites_count,
        )
