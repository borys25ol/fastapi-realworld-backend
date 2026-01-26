from datetime import datetime

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from conduit.core.exceptions import CommentNotFoundException
from conduit.domain.entities.comment import Comment as CommentEntity
from conduit.domain.repositories.comment import ICommentRepository
from conduit.infrastructure.mappers.comment_mapper import model_to_entity
from conduit.infrastructure.models import Comment


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, comment: CommentEntity) -> CommentEntity:
        query = (
            insert(Comment)
            .values(
                author_id=comment.author_id,
                article_id=comment.article_id,
                body=comment.body,
                created_at=comment.created_at,
                updated_at=comment.updated_at or comment.created_at,
            )
            .returning(Comment)
        )
        result = await self._session.execute(query)
        return model_to_entity(result.scalar_one())

    async def get_or_none(self, comment_id: int) -> CommentEntity | None:
        query = select(Comment).where(Comment.id == comment_id)
        if comment := await self._session.scalar(query):
            return model_to_entity(comment)

    async def get(self, comment_id: int) -> CommentEntity:
        query = select(Comment).where(Comment.id == comment_id)
        if not (comment := await self._session.scalar(query)):
            raise CommentNotFoundException()
        return model_to_entity(comment)

    async def list(self, article_id: int) -> list[CommentEntity]:
        query = select(Comment).where(Comment.article_id == article_id)
        comments = await self._session.scalars(query)
        return [model_to_entity(comment) for comment in comments]

    async def delete(self, comment_id: int) -> None:
        query = delete(Comment).where(Comment.id == comment_id)
        await self._session.execute(query)

    async def count(self, article_id: int) -> int:
        query = select(count(Comment.id)).where(Comment.article_id == article_id)
        result = await self._session.execute(query)
        return result.scalar_one()
