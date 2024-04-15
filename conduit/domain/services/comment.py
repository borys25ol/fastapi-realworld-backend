import abc
from typing import Any

from conduit.domain.dtos.comment import CommentDTO, CommentsListDTO, CreateCommentDTO
from conduit.domain.dtos.user import UserDTO


class ICommentService(abc.ABC):

    @abc.abstractmethod
    async def create_article_comment(
        self,
        session: Any,
        slug: str,
        comment_to_create: CreateCommentDTO,
        current_user: UserDTO,
    ) -> CommentDTO: ...

    @abc.abstractmethod
    async def get_article_comments(
        self, session: Any, slug: str, current_user: UserDTO | None
    ) -> CommentsListDTO: ...

    @abc.abstractmethod
    async def delete_article_comment(
        self, session: Any, slug: str, comment_id: int, current_user: UserDTO
    ) -> None: ...
