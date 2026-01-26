import abc

from conduit.domain.dtos.tag import TagRecordDTO


class IArticleTagRepository(abc.ABC):
    """Article Tag repository interface."""

    @abc.abstractmethod
    async def add_many(
        self, article_id: int, tags: list[str]
    ) -> list[TagRecordDTO]: ...

    @abc.abstractmethod
    async def list(self, article_id: int) -> list[TagRecordDTO]: ...
