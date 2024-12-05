import abc
from typing import Any

from conduit.domain.dtos.article import (
    ArticleDTO,
    ArticlesFeedDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
    ArticleVersionDTO,
)
from conduit.domain.dtos.user import UserDTO


class IArticleService(abc.ABC):

    @abc.abstractmethod
    async def create_new_article(
        self, session: Any, author_id: int, article_to_create: CreateArticleDTO
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def get_article_by_slug(
        self, session: Any, slug: str, current_user: UserDTO | None
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def delete_article_by_slug(
        self, session: Any, slug: str, current_user: UserDTO
    ) -> None: ...

    @abc.abstractmethod
    async def get_articles_feed(
        self, session: Any, current_user: UserDTO, limit: int, offset: int
    ) -> ArticlesFeedDTO: ...

    @abc.abstractmethod
    async def get_articles_feed_v2(
        self, session: Any, current_user: UserDTO, limit: int, offset: int
    ) -> ArticlesFeedDTO: ...

    @abc.abstractmethod
    async def get_articles_by_filters(
        self,
        session: Any,
        current_user: UserDTO | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> ArticlesFeedDTO: ...

    @abc.abstractmethod
    async def get_articles_by_filters_v2(
        self,
        session: Any,
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
        session: Any,
        slug: str,
        article_to_update: UpdateArticleDTO,
        current_user: UserDTO,
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def add_article_into_favorites(
        self, session: Any, slug: str, current_user: UserDTO
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def remove_article_from_favorites(
        self, session: Any, slug: str, current_user: UserDTO
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def create_draft(
        self,
        session: Any,
        author_id: int,
        draft_to_create: CreateArticleDTO,
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def publish_draft(
        self,
        session: Any,
        slug: str,
        current_user: UserDTO,
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def get_article_versions(
        self,
        session: Any,
        slug: str,
        current_user: UserDTO,
    ) -> list[ArticleVersionDTO]: ...

    @abc.abstractmethod
    async def list_user_drafts(
        self,
        session: Any,
        current_user: UserDTO,
        limit: int = 20,
        offset: int = 0,
    ) -> ArticlesFeedDTO: ...
