from dataclasses import asdict

from conduit.core.exceptions import (
    ArticleAlreadyFavoritedException,
    ArticleCreateException,
    ArticleNotFavoritedException,
    ArticlePermissionException,
)
from conduit.domain.dtos.article import (
    ArticleAuthorDTO,
    ArticleDTO,
    ArticleFeedRecordDTO,
    ArticleRecordDTO,
    ArticlesFeedDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
)
from conduit.domain.dtos.profile import ProfileDTO
from conduit.domain.dtos.user import UserDTO
from conduit.domain.services.article import IArticleService
from conduit.domain.services.profile import IProfileService
from conduit.domain.uow import IUnitOfWork


class ArticleService(IArticleService):
    """Service to handle articles logic."""

    def __init__(self, profile_service: IProfileService) -> None:
        self._profile_service = profile_service

    async def create_new_article(
        self, uow: IUnitOfWork, author_id: int, article_to_create: CreateArticleDTO
    ) -> ArticleDTO:
        try:
            article = await uow.articles.add(
                author_id=author_id, create_item=article_to_create
            )
        except Exception as exc:
            raise ArticleCreateException() from exc
        profile = await self._profile_service.get_profile_by_user_id(
            uow=uow, user_id=author_id
        )
        if article_to_create.tags:
            await uow.article_tags.add_many(
                article_id=article.id, tags=article_to_create.tags
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
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO | None
    ) -> ArticleDTO:
        article = await uow.articles.get_by_slug(slug=slug)
        profile = await self._profile_service.get_profile_by_user_id(
            uow=uow, user_id=article.author_id, current_user=current_user
        )
        return await self._get_article_info(
            uow=uow,
            article=article,
            profile=profile,
            user_id=current_user.id if current_user else None,
        )

    async def delete_article_by_slug(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO
    ) -> None:
        article = await uow.articles.get_by_slug(slug=slug)

        if article.author_id != current_user.id:
            raise ArticlePermissionException()

        await uow.articles.delete_by_slug(slug=slug)

    async def update_article_by_slug(
        self,
        uow: IUnitOfWork,
        slug: str,
        article_to_update: UpdateArticleDTO,
        current_user: UserDTO,
    ) -> ArticleDTO:
        article = await uow.articles.get_by_slug(slug=slug)

        if article.author_id != current_user.id:
            raise ArticlePermissionException()

        article = await uow.articles.update_by_slug(
            slug=slug, update_item=article_to_update
        )
        profile = await self._profile_service.get_profile_by_user_id(
            uow=uow, user_id=article.author_id, current_user=current_user
        )
        return await self._get_article_info(
            uow=uow, article=article, profile=profile, user_id=current_user.id
        )

    async def get_articles_by_filters(
        self,
        uow: IUnitOfWork,
        current_user: UserDTO | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> ArticlesFeedDTO:
        articles = await uow.articles.list_by_filters(
            user_id=current_user.id if current_user else None,
            limit=limit,
            offset=offset,
            tag=tag,
            author=author,
            favorited=favorited,
        )
        articles_with_extra = [
            self._to_article_dto_from_feed_record(article) for article in articles
        ]
        articles_count = await uow.articles.count_by_filters(
            tag=tag, author=author, favorited=favorited
        )
        return ArticlesFeedDTO(
            articles=articles_with_extra, articles_count=articles_count
        )

    async def get_articles_feed(
        self, uow: IUnitOfWork, current_user: UserDTO, limit: int, offset: int
    ) -> ArticlesFeedDTO:
        articles = await uow.articles.list_by_followings(
            user_id=current_user.id, limit=limit, offset=offset
        )
        articles_with_extra = [
            self._to_article_dto_from_feed_record(article) for article in articles
        ]
        articles_count = await uow.articles.count_by_followings(user_id=current_user.id)
        return ArticlesFeedDTO(
            articles=articles_with_extra, articles_count=articles_count
        )

    async def add_article_into_favorites(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO
    ) -> ArticleDTO:
        article = await self.get_article_by_slug(
            uow=uow, slug=slug, current_user=current_user
        )
        if article.favorited:
            raise ArticleAlreadyFavoritedException()

        await uow.favorites.create(article_id=article.id, user_id=current_user.id)
        return ArticleDTO.with_updated_fields(
            dto=article,
            updated_fields=dict(
                favorited=True, favorites_count=article.favorites_count + 1
            ),
        )

    async def remove_article_from_favorites(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO
    ) -> ArticleDTO:
        article = await self.get_article_by_slug(
            uow=uow, slug=slug, current_user=current_user
        )
        if not article.favorited:
            raise ArticleNotFavoritedException()

        await uow.favorites.delete(article_id=article.id, user_id=current_user.id)
        return ArticleDTO.with_updated_fields(
            dto=article,
            updated_fields=dict(
                favorited=False, favorites_count=article.favorites_count - 1
            ),
        )

    async def _get_article_info(
        self,
        uow: IUnitOfWork,
        article: ArticleRecordDTO,
        profile: ProfileDTO,
        user_id: int | None = None,
    ) -> ArticleDTO:
        article_tags = [
            tag.tag for tag in await uow.article_tags.list(article_id=article.id)
        ]
        favorites_count = await uow.favorites.count(article_id=article.id)
        is_favorited_by_user = (
            await uow.favorites.exists(author_id=user_id, article_id=article.id)
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
        uow: IUnitOfWork,
        articles: list[ArticleRecordDTO],
        current_user: UserDTO | None,
    ) -> dict[int, ProfileDTO]:
        following_profiles = await self._profile_service.get_profiles_by_user_ids(
            uow=uow,
            user_ids=[article.author_id for article in articles],
            current_user=current_user,
        )
        return {profile.user_id: profile for profile in following_profiles}

    @staticmethod
    def _to_article_dto_from_feed_record(record: ArticleFeedRecordDTO) -> ArticleDTO:
        return ArticleDTO(
            id=record.id,
            author_id=record.author_id,
            slug=record.slug,
            title=record.title,
            description=record.description,
            body=record.body,
            tags=record.tags,
            author=ArticleAuthorDTO(
                username=record.author_username,
                bio=record.author_bio or "",
                image=record.author_image_url,
                following=record.author_following,
            ),
            created_at=record.created_at,
            updated_at=record.updated_at,
            favorited=record.favorited,
            favorites_count=record.favorites_count,
        )
