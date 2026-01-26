from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conduit.domain.uow import IUnitOfWork
from conduit.infrastructure.repositories.article import ArticleRepository
from conduit.infrastructure.repositories.article_tag import ArticleTagRepository
from conduit.infrastructure.repositories.comment import CommentRepository
from conduit.infrastructure.repositories.favorite import FavoriteRepository
from conduit.infrastructure.repositories.follower import FollowerRepository
from conduit.infrastructure.repositories.tag import TagRepository
from conduit.infrastructure.repositories.user import UserRepository


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Unit of work that manages the SQLAlchemy async session."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self.users = UserRepository(self._session)
        self.articles = ArticleRepository(self._session)
        self.article_tags = ArticleTagRepository(self._session)
        self.comments = CommentRepository(self._session)
        self.favorites = FavoriteRepository(self._session)
        self.followers = FollowerRepository(self._session)
        self.tags = TagRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._session is None:
            return
        try:
            if exc:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._session.close()
            self._session = None

    async def commit(self) -> None:
        if self._session is None:
            return
        await self._session.commit()

    async def rollback(self) -> None:
        if self._session is None:
            return
        await self._session.rollback()
