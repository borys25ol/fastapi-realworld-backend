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
        return await self._get_article_info(
            session=session, article=article, user_id=user_id
        )

    async def get_articles_by_following_authors(
        self, session: AsyncSession, author_ids: list[int], user_id: int
    ) -> ArticlesFeedDTO:
        articles = await self._article_repo.get_by_author_ids(
            session=session, author_ids=author_ids
        )
        articles_count = await self._article_repo.count_by_author_ids(
            session=session, author_ids=author_ids
        )
        articles_with_extra = [
            await self._get_article_info(
                session=session, article=article, user_id=user_id
            )
            for article in articles
        ]
        return ArticlesFeedDTO(
            articles=articles_with_extra, articles_count=articles_count
        )

    async def _get_article_info(
        self, session: AsyncSession, article: ArticleDTO, user_id: int | None = None
    ) -> ArticleWithExtraDTO:
        article_tags = [
            tag.tag
            for tag in await self._article_tag_repo.get_by_article_id(
                session=session, article_id=article.id
            )
        ]
        favorites_count = await self._favorite_repo.count(
            session=session, article_id=article.id
        )
        is_favorited_by_user = (
            await self._favorite_repo.exists(
                session=session, author_id=user_id, article_id=article.id
            )
            if user_id
            else False
        )
        return ArticleWithExtraDTO(
            article=article,
            tags=article_tags,
            favorited=is_favorited_by_user,
            favorites_count=favorites_count,
        )
