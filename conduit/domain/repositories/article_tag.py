import abc
from typing import Any

from conduit.domain.dtos.tag import TagDTO


class IArticleTagRepository(abc.ABC):
    """Article Tag repository interface."""

    @abc.abstractmethod
    async def add_many(
        self, session: Any, article_id: int, tags: list[str]
    ) -> list[TagDTO]: ...

    @abc.abstractmethod
    async def list(self, session: Any, article_id: int) -> list[TagDTO]: ...
