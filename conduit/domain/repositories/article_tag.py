import abc
from typing import Any

from conduit.domain.dtos.tag import TagDTO


class IArticleTagRepository(abc.ABC):
    """Article Tag repository interface."""

    @abc.abstractmethod
    async def create_many(
        self, session: Any, article_id: int, tags: list[str]
    ) -> list[TagDTO]: ...

    @abc.abstractmethod
    async def get_all_by_article_id(
        self, session: Any, article_id: int
    ) -> list[TagDTO]: ...
