from datetime import datetime

from sqlalchemy import delete, exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from conduit.domain.repositories.favorite import IFavoriteRepository
from conduit.infrastructure.models import Favorite


class FavoriteRepository(IFavoriteRepository):
    """Repository for Follower model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, author_id: int, article_id: int) -> bool:
        query = (
            exists()
            .where(Favorite.user_id == author_id, Favorite.article_id == article_id)
            .select()
        )
        result = await self._session.execute(query)
        return result.scalar_one() is True

    async def count(self, article_id: int) -> int:
        query = select(count()).where(Favorite.article_id == article_id)
        result = await self._session.execute(query)
        return int(result.scalar_one())

    async def create(self, article_id: int, user_id: int) -> None:
        query = insert(Favorite).values(
            user_id=user_id, article_id=article_id, created_at=datetime.now()
        )
        await self._session.execute(query)

    async def delete(self, article_id: int, user_id: int) -> None:
        query = delete(Favorite).where(
            Favorite.user_id == user_id, Favorite.article_id == article_id
        )
        await self._session.execute(query)
