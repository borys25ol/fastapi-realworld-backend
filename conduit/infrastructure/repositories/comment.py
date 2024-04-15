from datetime import datetime

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from conduit.domain.dtos.comment import CommentRecordDTO, CreateCommentDTO
from conduit.domain.mapper import IModelMapper
from conduit.domain.repositories.comment import ICommentRepository
from conduit.infrastructure.models import Comment


class CommentRepository(ICommentRepository):

    def __init__(self, comment_mapper: IModelMapper[Comment, CommentRecordDTO]):
        self._comment_mapper = comment_mapper

    async def create(
        self,
        session: AsyncSession,
        author_id: int,
        article_id: int,
        create_item: CreateCommentDTO,
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
        result = await session.execute(query)
        return self._comment_mapper.to_dto(result.scalar())

    async def get_by_id(
        self, session: AsyncSession, comment_id: int
    ) -> CommentRecordDTO | None:
        query = select(Comment).where(Comment.id == comment_id)
        if comment := await session.scalar(query):
            return self._comment_mapper.to_dto(comment)

    async def get_all_by_article_id(
        self, session: AsyncSession, article_id: int
    ) -> list[CommentRecordDTO]:
        query = select(Comment).where(Comment.article_id == article_id)
        comments = await session.scalars(query)
        return [self._comment_mapper.to_dto(comment) for comment in comments]

    async def delete_by_id(self, session: AsyncSession, comment_id: int) -> None:
        query = delete(Comment).where(Comment.id == comment_id)
        await session.execute(query)

    async def count_by_article_id(self, session: AsyncSession, article_id: int) -> int:
        query = select(count(Comment.id)).where(Comment.article_id == article_id)
        result = await session.execute(query)
        return result.scalar()
