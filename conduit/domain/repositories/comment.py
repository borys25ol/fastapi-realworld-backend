import abc
from typing import Any

from conduit.domain.dtos.comment import CommentRecordDTO, CreateCommentDTO


class ICommentRepository(abc.ABC):
    """Comment repository interface."""

    @abc.abstractmethod
    async def add(
        self,
        session: Any,
        author_id: int,
        article_id: int,
        create_item: CreateCommentDTO,
    ) -> CommentRecordDTO: ...

    @abc.abstractmethod
    async def get_or_none(
        self, session: Any, comment_id: int
    ) -> CommentRecordDTO | None: ...

    @abc.abstractmethod
    async def get(self, session: Any, comment_id: int) -> CommentRecordDTO: ...

    @abc.abstractmethod
    async def list(self, session: Any, article_id: int) -> list[CommentRecordDTO]: ...

    @abc.abstractmethod
    async def delete(self, session: Any, comment_id: int) -> None: ...

    @abc.abstractmethod
    async def count(self, session: Any, article_id: int) -> int: ...
