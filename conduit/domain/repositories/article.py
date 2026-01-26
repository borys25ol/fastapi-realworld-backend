import abc

from conduit.domain.dtos.article import (
    ArticleFeedRecordDTO,
    ArticleRecordDTO,
    CreateArticleDTO,
    UpdateArticleDTO,
)


class IArticleRepository(abc.ABC):
    """Article repository interface."""

    @abc.abstractmethod
    async def add(
        self, author_id: int, create_item: CreateArticleDTO
    ) -> ArticleRecordDTO: ...

    @abc.abstractmethod
    async def get_by_slug_or_none(self, slug: str) -> ArticleRecordDTO | None: ...

    @abc.abstractmethod
    async def get_by_slug(self, slug: str) -> ArticleRecordDTO: ...

    @abc.abstractmethod
    async def delete_by_slug(self, slug: str) -> None: ...

    @abc.abstractmethod
    async def update_by_slug(
        self, slug: str, update_item: UpdateArticleDTO
    ) -> ArticleRecordDTO: ...

    @abc.abstractmethod
    async def list_by_followings(
        self, user_id: int, limit: int, offset: int
    ) -> list[ArticleFeedRecordDTO]: ...

    @abc.abstractmethod
    async def list_by_filters(
        self,
        user_id: int | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> list[ArticleFeedRecordDTO]: ...

    @abc.abstractmethod
    async def count_by_followings(self, user_id: int) -> int: ...

    @abc.abstractmethod
    async def count_by_filters(
        self,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> int: ...
