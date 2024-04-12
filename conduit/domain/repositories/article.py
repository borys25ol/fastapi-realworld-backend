import abc
from typing import Any

from conduit.domain.dtos.article import ArticleDTO, CreateArticleDTO, UpdateArticleDTO


class IArticleRepository(abc.ABC):
    """Article repository interface."""

    @abc.abstractmethod
    async def create(
        self, session: Any, author_id: int, create_item: CreateArticleDTO
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def get_by_slug(self, session: Any, slug: str) -> ArticleDTO | None: ...

    @abc.abstractmethod
    async def delete_by_slug(self, session: Any, slug: str) -> None: ...

    @abc.abstractmethod
    async def update_by_slug(
        self, session: Any, slug: str, update_item: UpdateArticleDTO
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def get_all_by_following_profiles(
        self, session: Any, user_id: int, limit: int, offset: int
    ) -> list[ArticleDTO]: ...

    @abc.abstractmethod
    async def get_all_by_filters(
        self,
        session: Any,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> list[ArticleDTO]: ...

    @abc.abstractmethod
    async def count_by_following_profiles(self, session: Any, user_id: int) -> int: ...

    @abc.abstractmethod
    async def count_by_filters(
        self,
        session: Any,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> int: ...
