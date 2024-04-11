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
    async def get_by_author_ids(
        self, session: Any, author_ids: list[int]
    ) -> list[ArticleDTO]: ...

    @abc.abstractmethod
    async def get_all(self, session: Any) -> list[ArticleDTO]: ...

    @abc.abstractmethod
    async def count_by_author_ids(self, session: Any, author_ids: list[int]) -> int: ...

    @abc.abstractmethod
    async def count_all(self, session: Any) -> int: ...
