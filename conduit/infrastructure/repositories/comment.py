from datetime import datetime

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from conduit.core.exceptions import CommentNotFoundException
from conduit.domain.dtos.comment import CommentRecordDTO, CreateCommentDTO
from conduit.domain.repositories.comment import ICommentRepository
from conduit.infrastructure.models import Comment


class CommentRepository(ICommentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_comment_record_dto(model: Comment) -> CommentRecordDTO:
        return CommentRecordDTO(
            id=model.id,
            body=model.body,
            author_id=model.author_id,
            article_id=model.article_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def add(
        self, author_id: int, article_id: int, create_item: CreateCommentDTO
    ) -> CommentRecordDTO:
        query = (
            insert(Comment)
            .values(
                author_id=author_id,
                article_id=article_id,
                body=create_item.body,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            .returning(Comment)
        )
        result = await self._session.execute(query)
        return self._to_comment_record_dto(result.scalar_one())

    async def get_or_none(self, comment_id: int) -> CommentRecordDTO | None:
        query = select(Comment).where(Comment.id == comment_id)
        if comment := await self._session.scalar(query):
            return self._to_comment_record_dto(comment)

    async def get(self, comment_id: int) -> CommentRecordDTO:
        query = select(Comment).where(Comment.id == comment_id)
        if not (comment := await self._session.scalar(query)):
            raise CommentNotFoundException()
        return self._to_comment_record_dto(comment)

    async def list(self, article_id: int) -> list[CommentRecordDTO]:
        query = select(Comment).where(Comment.article_id == article_id)
        comments = await self._session.scalars(query)
        return [self._to_comment_record_dto(comment) for comment in comments]

    async def delete(self, comment_id: int) -> None:
        query = delete(Comment).where(Comment.id == comment_id)
        await self._session.execute(query)

    async def count(self, article_id: int) -> int:
        query = select(count(Comment.id)).where(Comment.article_id == article_id)
        result = await self._session.execute(query)
        return result.scalar_one()
