import abc

from conduit.domain.entities.tag import Tag


class IArticleTagRepository(abc.ABC):
    """Article Tag repository interface."""

    @abc.abstractmethod
    async def add_many(self, article_id: int, tags: list[str]) -> list[Tag]: ...

    @abc.abstractmethod
    async def list(self, article_id: int) -> list[Tag]: ...
