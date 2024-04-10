import abc
from typing import Any

from conduit.domain.dtos.tag import TagDTO


class IArticleTagRepository(abc.ABC):
    """Article Tag repository interface."""

    @abc.abstractmethod
    async def create(
        self, session: Any, article_id: int, tags: list[TagDTO]
    ) -> None: ...

    @abc.abstractmethod
    async def get_by_article_id(
        self, session: Any, article_id: int
    ) -> list[TagDTO]: ...
