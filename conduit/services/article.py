from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import (
    ArticleAlreadyFavoritedException,
    ArticleNotFavoritedException,
    ArticlePermissionException,
)
from conduit.domain.dtos.article import (
    ArticleAuthorDTO,
    ArticleDTO,
    ArticleRecordDTO,
    ArticlesFeedDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
    ArticleVersionDTO,
)
from conduit.domain.dtos.profile import ProfileDTO
from conduit.domain.dtos.user import UserDTO
from conduit.domain.repositories.article import IArticleRepository
from conduit.domain.repositories.article_tag import IArticleTagRepository
from conduit.domain.repositories.favorite import IFavoriteRepository
from conduit.domain.services.article import IArticleService
from conduit.domain.services.profile import IProfileService


class ArticleService(IArticleService):
    """Service to handle articles logic."""

    def __init__(
        self,
        article_repo: IArticleRepository,
        article_tag_repo: IArticleTagRepository,
        favorite_repo: IFavoriteRepository,
        profile_service: IProfileService,
    ) -> None:
        self._article_repo = article_repo
        self._article_tag_repo = article_tag_repo
        self._favorite_repo = favorite_repo
        self._profile_service = profile_service

    async def create_new_article(
        self, session: AsyncSession, author_id: int, article_to_create: CreateArticleDTO
    ) -> ArticleDTO:
        article = await self._article_repo.add(
            session=session, author_id=author_id, create_item=article_to_create
        )
        profile = await self._profile_service.get_profile_by_user_id(
            session=session, user_id=author_id
        )
        if article_to_create.tags:
            await self._article_tag_repo.add_many(
                session=session, article_id=article.id, tags=article_to_create.tags
            )
        return ArticleDTO(
            **asdict(article),
            author=ArticleAuthorDTO(
                username=profile.username,
                bio=profile.bio,
                image=profile.image,
                following=profile.following,
            ),
            tags=article_to_create.tags,
            favorited=False,
            favorites_count=0,
        )

    async def get_article_by_slug(
        self, session: AsyncSession, slug: str, current_user: UserDTO | None
    ) -> ArticleDTO:
        article = await self._article_repo.get_by_slug(session=session, slug=slug)
        profile = await self._profile_service.get_profile_by_user_id(
            session=session, user_id=article.author_id, current_user=current_user
        )
        return await self._get_article_info(
            session=session,
            article=article,
            profile=profile,
            user_id=current_user.id if current_user else None,
        )

    async def delete_article_by_slug(
        self, session: AsyncSession, slug: str, current_user: UserDTO
    ) -> None:
        article = await self._article_repo.get_by_slug(session=session, slug=slug)

        if article.author_id != current_user.id:
            raise ArticlePermissionException()

        await self._article_repo.delete_by_slug(session=session, slug=slug)

    async def update_article_by_slug(
        self,
        session: AsyncSession,
        slug: str,
        article_to_update: UpdateArticleDTO,
        current_user: UserDTO,
    ) -> ArticleDTO:
        article = await self._article_repo.get_by_slug(session=session, slug=slug)

        if article.author_id != current_user.id:
            raise ArticlePermissionException()

        article = await self._article_repo.update_by_slug(
            session=session, slug=slug, update_item=article_to_update
        )
        profile = await self._profile_service.get_profile_by_user_id(
            session=session, user_id=article.author_id, current_user=current_user
        )
        return await self._get_article_info(
            session=session, article=article, profile=profile, user_id=current_user.id
        )

    async def get_articles_by_filters(
        self,
        session: AsyncSession,
        current_user: UserDTO | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> ArticlesFeedDTO:
        articles = await self._article_repo.list_by_filters(
            session=session,
            limit=limit,
            offset=offset,
            tag=tag,
            author=author,
            favorited=favorited,
        )
        profiles_map = await self._get_profiles_mapping(
            session=session, articles=articles, current_user=current_user
        )
        articles_with_extra = [
            await self._get_article_info(
                session=session,
                article=article,
                profile=profiles_map[article.author_id],
                user_id=current_user.id if current_user else None,
            )
            for article in articles
        ]
        articles_count = await self._article_repo.count_by_filters(
            session=session, tag=tag, author=author, favorited=favorited
        )
        return ArticlesFeedDTO(
            articles=articles_with_extra, articles_count=articles_count
        )

    async def get_articles_by_filters_v2(
        self,
        session: AsyncSession,
        current_user: UserDTO | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> ArticlesFeedDTO:
        articles = await self._article_repo.list_by_filters_v2(
            session=session,
            user_id=current_user.id if current_user else None,
            limit=limit,
            offset=offset,
            tag=tag,
            author=author,
            favorited=favorited,
        )
        articles_count = await self._article_repo.count_by_filters(
            session=session, tag=tag, author=author, favorited=favorited
        )
        return ArticlesFeedDTO(articles=articles, articles_count=articles_count)

    async def get_articles_feed(
        self, session: AsyncSession, current_user: UserDTO, limit: int, offset: int
    ) -> ArticlesFeedDTO:
        articles = await self._article_repo.list_by_followings(
            session=session, user_id=current_user.id, limit=limit, offset=offset
        )
        profiles_map = await self._get_profiles_mapping(
            session=session, articles=articles, current_user=current_user
        )
        articles_with_extra = [
            await self._get_article_info(
                session=session,
                article=article,
                profile=profiles_map[article.author_id],
                user_id=current_user.id,
            )
            for article in articles
        ]
        articles_count = await self._article_repo.count_by_followings(
            session=session, user_id=current_user.id
        )
        return ArticlesFeedDTO(
            articles=articles_with_extra, articles_count=articles_count
        )

    async def get_articles_feed_v2(
        self, session: AsyncSession, current_user: UserDTO, limit: int, offset: int
    ) -> ArticlesFeedDTO:
        articles = await self._article_repo.list_by_followings_v2(
            session=session, user_id=current_user.id, limit=limit, offset=offset
        )
        articles_count = await self._article_repo.count_by_followings(
            session=session, user_id=current_user.id
        )
        return ArticlesFeedDTO(articles=articles, articles_count=articles_count)

    async def add_article_into_favorites(
        self, session: AsyncSession, slug: str, current_user: UserDTO
    ) -> ArticleDTO:
        article = await self.get_article_by_slug(
            session=session, slug=slug, current_user=current_user
        )
        if article.favorited:
            raise ArticleAlreadyFavoritedException()

        await self._favorite_repo.create(
            session=session, article_id=article.id, user_id=current_user.id
        )
        return ArticleDTO.with_updated_fields(
            dto=article,
            updated_fields=dict(
                favorited=True, favorites_count=article.favorites_count + 1
            ),
        )

    async def remove_article_from_favorites(
        self, session: AsyncSession, slug: str, current_user: UserDTO
    ) -> ArticleDTO:
        article = await self.get_article_by_slug(
            session=session, slug=slug, current_user=current_user
        )
        if not article.favorited:
            raise ArticleNotFavoritedException()

        await self._favorite_repo.delete(
            session=session, article_id=article.id, user_id=current_user.id
        )
        return ArticleDTO.with_updated_fields(
            dto=article,
            updated_fields=dict(
                favorited=False, favorites_count=article.favorites_count - 1
            ),
        )

    async def _get_article_info(
        self,
        session: AsyncSession,
        article: ArticleRecordDTO,
        profile: ProfileDTO,
        user_id: int | None = None,
    ) -> ArticleDTO:
        article_tags = [
            tag.tag
            for tag in await self._article_tag_repo.list(
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
        return ArticleDTO(
            **asdict(article),
            author=ArticleAuthorDTO(
                username=profile.username,
                bio=profile.bio,
                image=profile.image,
                following=profile.following,
            ),
            tags=article_tags,
            favorited=is_favorited_by_user,
            favorites_count=favorites_count,
        )

    async def _get_profiles_mapping(
        self,
        session: AsyncSession,
        articles: list[ArticleRecordDTO],
        current_user: UserDTO | None,
    ) -> dict[int, ProfileDTO]:
        following_profiles = await self._profile_service.get_profiles_by_user_ids(
            session=session,
            user_ids=[article.author_id for article in articles],
            current_user=current_user,
        )
        return {profile.user_id: profile for profile in following_profiles}

    async def create_draft(
        self,
        session: AsyncSession,
        author_id: int,
        draft_to_create: CreateArticleDTO,
    ) -> ArticleDTO:
        article = await self._article_repo.add_draft(
            session=session, author_id=author_id, create_item=draft_to_create
        )
        profile = await self._profile_service.get_profile_by_user_id(
            session=session, user_id=author_id
        )
        if draft_to_create.tags:
            await self._article_tag_repo.add_many(
                session=session, article_id=article.id, tags=draft_to_create.tags
            )
        return await self._get_article_info(
            session=session, article=article, profile=profile, user_id=author_id
        )

    async def publish_draft(
        self,
        session: AsyncSession,
        slug: str,
        current_user: UserDTO,
    ) -> ArticleDTO:
        article = await self._article_repo.get_by_slug(session=session, slug=slug)
        
        if article.author_id != current_user.id:
            raise ArticlePermissionException()
        
        article = await self._article_repo.publish_draft(
            session=session, slug=slug, author_id=current_user.id
        )
        profile = await self._profile_service.get_profile_by_user_id(
            session=session, user_id=article.author_id, current_user=current_user
        )
        return await self._get_article_info(
            session=session, article=article, profile=profile, user_id=current_user.id
        )

    async def get_article_versions(
        self,
        session: AsyncSession,
        slug: str,
        current_user: UserDTO,
    ) -> list[ArticleVersionDTO]:
        article = await self._article_repo.get_by_slug(session=session, slug=slug)
        
        if article.author_id != current_user.id:
            raise ArticlePermissionException()
        
        return await self._article_repo.get_versions(
            session=session, slug=slug, author_id=current_user.id
        )

    async def list_user_drafts(
        self,
        session: AsyncSession,
        current_user: UserDTO,
        limit: int = 20,
        offset: int = 0,
    ) -> ArticlesFeedDTO:
        articles = await self._article_repo.list_drafts(
            session=session,
            author_id=current_user.id,
            limit=limit,
            offset=offset
        )
        count = len(articles)  # For drafts, we can use the actual list length
        return ArticlesFeedDTO(articles=articles, articles_count=count)
