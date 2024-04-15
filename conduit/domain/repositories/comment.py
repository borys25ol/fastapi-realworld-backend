import abc
from typing import Any

from conduit.domain.dtos.comment import CommentRecordDTO, CreateCommentDTO


class ICommentRepository(abc.ABC):
    """Comment repository interface."""

    @abc.abstractmethod
    async def create(
        self,
        session: Any,
        author_id: int,
        article_id: int,
        create_item: CreateCommentDTO,
    ) -> CommentRecordDTO: ...

    @abc.abstractmethod
    async def get_by_id(
        self, session: Any, comment_id: int
    ) -> CommentRecordDTO | None: ...

    @abc.abstractmethod
    async def get_all_by_article_id(
        self, session: Any, article_id: int
    ) -> list[CommentRecordDTO]: ...

    @abc.abstractmethod
    async def delete_by_id(self, session: Any, comment_id: int) -> None: ...

    @abc.abstractmethod
    async def count_by_article_id(self, session: Any, article_id: int) -> int: ...
