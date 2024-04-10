from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.dtos.article import (
    ArticleDTO,
    ArticlesFeedDTO,
    ArticleWithExtraDTO,
    CreateArticleDTO,
)
from conduit.domain.repositories.article import IArticleRepository
from conduit.domain.repositories.article_tag import IArticleTagRepository
from conduit.domain.repositories.favorite import IFavoriteRepository
from conduit.domain.repositories.tag import ITagRepository
from conduit.domain.services.article import IArticleService


class ArticleService(IArticleService):
    """Service to handle articles logic."""

    def __init__(
        self,
        tag_repo: ITagRepository,
        article_repo: IArticleRepository,
        article_tag_repo: IArticleTagRepository,
        favorite_repo: IFavoriteRepository,
    ) -> None:
        self._tag_repo = tag_repo
        self._article_repo = article_repo
        self._article_tag_repo = article_tag_repo
        self._favorite_repo = favorite_repo

    async def create_new_article(
        self, session: AsyncSession, author_id: int, article_to_create: CreateArticleDTO
    ) -> ArticleWithExtraDTO:
        article = await self._article_repo.create(
            session=session, author_id=author_id, create_item=article_to_create
        )
        tags = await self._tag_repo.create(session=session, tags=article_to_create.tags)

        # Associate tags with the article.
        await self._article_tag_repo.create(
            session=session, article_id=article.id, tags=tags
        )
        return ArticleWithExtraDTO(
            article=article,
            tags=article_to_create.tags,
            favorited=False,
            favorites_count=0,
        )

    async def get_article_by_slug(
        self, session: AsyncSession, slug: str, user_id: int | None = None
    ) -> ArticleWithExtraDTO:
        article = await self._article_repo.get_by_slug(session=session, slug=slug)
        article_tags = await self._article_tag_repo.get_by_article_id(
            session=session, article_id=article.id
        )
        favorites_count = await self._favorite_repo.count(
            session=session, article_id=article.id
        )
        is_favorite_by_user = (
            await self._favorite_repo.exists(
                session=session, author_id=user_id, article_id=article.id
            )
            if user_id
            else False
        )
        return ArticleWithExtraDTO(
            article=article,
            tags=[tag.tag for tag in article_tags],
            favorited=is_favorite_by_user,
            favorites_count=favorites_count,
        )

    async def get_articles_by_following_authors(
        self, session: AsyncSession, following_author_ids: list[int]
    ) -> ArticlesFeedDTO:
        articles = await self._article_repo.get_by_author_ids(
            session=session, author_ids=following_author_ids
        )
        articles_with_extra = [
            await self._get_following_article_info(session=session, article=article)
            for article in articles
        ]
        return ArticlesFeedDTO(
            articles=articles_with_extra, articles_count=len(articles_with_extra)
        )

    async def _get_following_article_info(
        self, session: AsyncSession, article: ArticleDTO
    ) -> ArticleWithExtraDTO:
        article_tags = await self._article_tag_repo.get_by_article_id(
            session=session, article_id=article.id
        )
        favorites_count = await self._favorite_repo.count(
            session=session, article_id=article.id
        )
        is_favorite_by_user = await self._favorite_repo.exists(
            session=session, author_id=article.author_id, article_id=article.id
        )
        return ArticleWithExtraDTO(
            article=article,
            tags=[tag.tag for tag in article_tags],
            favorited=is_favorite_by_user,
            favorites_count=favorites_count,
        )
