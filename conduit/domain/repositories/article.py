import abc
from typing import Any

from conduit.domain.dtos.article import (
    ArticleDTO,
    ArticleRecordDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
    ArticleVersionDTO,
)


class IArticleRepository(abc.ABC):
    """Article repository interface."""

    @abc.abstractmethod
    async def add(
        self, session: Any, author_id: int, create_item: CreateArticleDTO
    ) -> ArticleRecordDTO: ...

    @abc.abstractmethod
    async def get_by_slug_or_none(
        self, session: Any, slug: str
    ) -> ArticleRecordDTO | None: ...

    @abc.abstractmethod
    async def get_by_slug(self, session: Any, slug: str) -> ArticleRecordDTO: ...

    @abc.abstractmethod
    async def delete_by_slug(self, session: Any, slug: str) -> None: ...

    @abc.abstractmethod
    async def update_by_slug(
        self, session: Any, slug: str, update_item: UpdateArticleDTO
    ) -> ArticleRecordDTO: ...

    @abc.abstractmethod
    async def list_by_followings(
        self, session: Any, user_id: int, limit: int, offset: int
    ) -> list[ArticleRecordDTO]: ...

    @abc.abstractmethod
    async def list_by_followings_v2(
        self, session: Any, user_id: int, limit: int, offset: int
    ) -> list[ArticleDTO]: ...

    @abc.abstractmethod
    async def list_by_filters(
        self,
        session: Any,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> list[ArticleRecordDTO]: ...

    @abc.abstractmethod
    async def list_by_filters_v2(
        self,
        session: Any,
        user_id: int | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> list[ArticleDTO]: ...

    @abc.abstractmethod
    async def count_by_followings(self, session: Any, user_id: int) -> int: ...

    @abc.abstractmethod
    async def count_by_filters(
        self,
        session: Any,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> int: ...

    @abc.abstractmethod
    async def add_draft(
        self, session: Any, author_id: int, create_item: CreateArticleDTO
    ) -> ArticleRecordDTO: ...

    @abc.abstractmethod
    async def publish_draft(
        self, session: Any, slug: str, author_id: int
    ) -> ArticleRecordDTO: ...

    @abc.abstractmethod
    async def get_versions(
        self, session: Any, slug: str, author_id: int
    ) -> list[ArticleVersionDTO]: ...

    @abc.abstractmethod
    async def list_drafts(
        self, session: Any, author_id: int, limit: int, offset: int
    ) -> list[ArticleDTO]: ...
