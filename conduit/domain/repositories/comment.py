import abc

from conduit.domain.dtos.comment import CreateCommentDTO
from conduit.domain.entities.comment import Comment


class ICommentRepository(abc.ABC):
    """Comment repository interface."""

    @abc.abstractmethod
    async def add(
        self, author_id: int, article_id: int, create_item: CreateCommentDTO
    ) -> Comment: ...

    @abc.abstractmethod
    async def get_or_none(self, comment_id: int) -> Comment | None: ...

    @abc.abstractmethod
    async def get(self, comment_id: int) -> Comment: ...

    @abc.abstractmethod
    async def list(self, article_id: int) -> list[Comment]: ...

    @abc.abstractmethod
    async def delete(self, comment_id: int) -> None: ...

    @abc.abstractmethod
    async def count(self, article_id: int) -> int: ...
