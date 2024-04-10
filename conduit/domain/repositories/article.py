import abc
from typing import Any

from conduit.domain.dtos.article import ArticleDTO, CreateArticleDTO


class IArticleRepository(abc.ABC):
    """Article repository interface."""

    @abc.abstractmethod
    async def create(
        self, session: Any, author_id: int, create_item: CreateArticleDTO
    ) -> ArticleDTO: ...

    @abc.abstractmethod
    async def get_by_slug(self, session: Any, slug: str) -> ArticleDTO: ...

    @abc.abstractmethod
    async def get_by_author_ids(
        self, session: Any, author_ids: list[int]
    ) -> list[ArticleDTO]: ...

    @abc.abstractmethod
    async def count_by_author_ids(self, session: Any, author_ids: list[int]) -> int: ...
