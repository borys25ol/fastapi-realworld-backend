from datetime import datetime

from conduit.application.dtos.article import (
    ArticleDTO,
    ArticlesFeedDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
)
from conduit.application.dtos.profile import ProfileDTO
from conduit.application.dtos.user import UserDTO
from conduit.application.mappers.article_mapper import (
    entity_to_article_dto,
    feed_record_to_article_dto,
    feed_records_to_articles_dto,
)
from conduit.application.queries.article_feed import ArticleFeedRecordDTO
from conduit.application.services.article import IArticleService
from conduit.application.services.profile import IProfileService
from conduit.core.exceptions import ArticleCreateException
from conduit.core.utils.slug import make_slug_from_title
from conduit.domain.entities.article import Article
from conduit.domain.entities.favorite import Favorite
from conduit.domain.uow import IUnitOfWork


class ArticleService(IArticleService):
    """Service to handle articles logic."""

    def __init__(self, profile_service: IProfileService) -> None:
        self._profile_service = profile_service

    async def create_new_article(
        self, uow: IUnitOfWork, author_id: int, article_to_create: CreateArticleDTO
    ) -> ArticleDTO:
        try:
            article = Article(
                id=0,
                author_id=author_id,
                slug=make_slug_from_title(title=article_to_create.title),
                title=article_to_create.title,
                description=article_to_create.description,
                body=article_to_create.body,
                created_at=datetime.now(),
                updated_at=None,
            )
            article = await uow.articles.add(article)
        except Exception as exc:
            raise ArticleCreateException() from exc
        profile = await self._profile_service.get_profile_by_user_id(
            uow=uow, user_id=author_id
        )
        if article_to_create.tags:
            await uow.article_tags.add_many(
                article_id=article.id, tags=article_to_create.tags
            )
        return entity_to_article_dto(
            article=article,
            profile=profile,
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

        article.assert_owner(user_id=current_user.id)

        await uow.articles.delete_by_slug(slug=slug)

    async def update_article_by_slug(
        self,
        uow: IUnitOfWork,
        slug: str,
        article_to_update: UpdateArticleDTO,
        current_user: UserDTO,
    ) -> ArticleDTO:
        article = await uow.articles.get_by_slug(slug=slug)

        article.assert_owner(user_id=current_user.id)

        article.update_content(
            title=article_to_update.title,
            description=article_to_update.description,
            body=article_to_update.body,
        )
        article = await uow.articles.update_by_slug(slug=slug, article=article)
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
        articles_count = await uow.articles.count_by_filters(
            tag=tag, author=author, favorited=favorited
        )
        return feed_records_to_articles_dto(
            records=articles, articles_count=articles_count
        )

    async def get_articles_feed(
        self, uow: IUnitOfWork, current_user: UserDTO, limit: int, offset: int
    ) -> ArticlesFeedDTO:
        articles = await uow.articles.list_by_followings(
            user_id=current_user.id, limit=limit, offset=offset
        )
        articles_count = await uow.articles.count_by_followings(user_id=current_user.id)
        return feed_records_to_articles_dto(
            records=articles, articles_count=articles_count
        )

    async def add_article_into_favorites(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO
    ) -> ArticleDTO:
        article = await self.get_article_by_slug(
            uow=uow, slug=slug, current_user=current_user
        )
        favorite = Favorite(
            user_id=current_user.id,
            article_id=article.id,
            created_at=article.updated_at or article.created_at,
        )
        favorite.assert_not_favorited(is_favorited=article.favorited)

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
        favorite = Favorite(
            user_id=current_user.id,
            article_id=article.id,
            created_at=article.updated_at or article.created_at,
        )
        favorite.assert_favorited(is_favorited=article.favorited)

        await uow.favorites.delete(article_id=article.id, user_id=current_user.id)
        return ArticleDTO.with_updated_fields(
            dto=article,
            updated_fields=dict(
                favorited=False, favorites_count=article.favorites_count - 1
            ),
        )

    @staticmethod
    async def _get_article_info(
        uow: IUnitOfWork,
        article: Article,
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
        return entity_to_article_dto(
            article=article,
            profile=profile,
            tags=article_tags,
            favorited=is_favorited_by_user,
            favorites_count=favorites_count,
        )

    @staticmethod
    def _to_article_dto_from_feed_record(record: ArticleFeedRecordDTO) -> ArticleDTO:
        return feed_record_to_article_dto(record=record)
