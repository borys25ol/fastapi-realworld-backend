import abc

from conduit.application.dtos.article import (
    ArticleDTO,
    ArticlesFeedDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
)
from conduit.application.dtos.user import UserDTO
from conduit.domain.uow import IUnitOfWork


class IArticleService(abc.ABC):
    @abc.abstractmethod
    async def create_new_article(
        self, uow: IUnitOfWork, author_id: int, article_to_create: CreateArticleDTO
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def get_article_by_slug(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO | None
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def delete_article_by_slug(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO
    ) -> None: ...

    @abc.abstractmethod
    async def get_articles_feed(
        self, uow: IUnitOfWork, current_user: UserDTO, limit: int, offset: int
    ) -> ArticlesFeedDTO: ...

    @abc.abstractmethod
    async def get_articles_by_filters(
        self,
        uow: IUnitOfWork,
        current_user: UserDTO | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> ArticlesFeedDTO: ...

    @abc.abstractmethod
    async def update_article_by_slug(
        self,
        uow: IUnitOfWork,
        slug: str,
        article_to_update: UpdateArticleDTO,
        current_user: UserDTO,
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def add_article_into_favorites(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def remove_article_from_favorites(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO
    ) -> ArticleDTO: ...
