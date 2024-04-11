import abc
from typing import Any

from conduit.domain.dtos.article import (
    ArticlesFeedDTO,
    ArticleWithExtraDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
)
from conduit.domain.dtos.user import UserDTO


class IArticleService(abc.ABC):

    @abc.abstractmethod
    async def create_new_article(
        self, session: Any, author_id: int, article_to_create: CreateArticleDTO
    ) -> ArticleWithExtraDTO: ...

    @abc.abstractmethod
    async def get_article_by_slug(
        self, session: Any, slug: str, current_user: UserDTO | None
    ) -> ArticleWithExtraDTO: ...

    @abc.abstractmethod
    async def delete_article_by_slug(
        self, session: Any, slug: str, current_user: UserDTO
    ) -> None: ...

    @abc.abstractmethod
    async def get_articles_by_following_authors(
        self, session: Any, current_user: UserDTO
    ) -> ArticlesFeedDTO: ...

    @abc.abstractmethod
    async def get_global_articles(
        self, session: Any, current_user: UserDTO
    ) -> ArticlesFeedDTO: ...

    @abc.abstractmethod
    async def update_article_by_slug(
        self,
        session: Any,
        slug: str,
        article_to_update: UpdateArticleDTO,
        current_user: UserDTO,
    ) -> ArticleWithExtraDTO: ...

    @abc.abstractmethod
    async def add_article_into_favorites(
        self, session: Any, slug: str, current_user: UserDTO
    ) -> ArticleWithExtraDTO: ...

    @abc.abstractmethod
    async def remove_article_from_favorites(
        self, session: Any, slug: str, current_user: UserDTO
    ) -> ArticleWithExtraDTO: ...
