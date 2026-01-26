from datetime import datetime

from sqlalchemy import delete, exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.repositories.follower import IFollowerRepository
from conduit.infrastructure.models import Follower


class FollowerRepository(IFollowerRepository):
    """Repository for Follower model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, follower_id: int, following_id: int) -> bool:
        query = (
            exists()
            .where(
                Follower.follower_id == follower_id,
                Follower.following_id == following_id,
            )
            .select()
        )
        result = await self._session.execute(query)
        return result.scalar_one() is True

    async def list(self, follower_id: int, following_ids: list[int]) -> list[int]:
        query = select(Follower.following_id).where(
            Follower.following_id.in_(following_ids),
            Follower.follower_id == follower_id,
        )
        result = await self._session.execute(query)
        return list(result.scalars())

    async def create(self, follower_id: int, following_id: int) -> None:
        query = insert(Follower).values(
            follower_id=follower_id,
            following_id=following_id,
            created_at=datetime.now(),
        )
        await self._session.execute(query)

    async def delete(self, follower_id: int, following_id: int) -> None:
        query = delete(Follower).where(
            Follower.follower_id == follower_id, Follower.following_id == following_id
        )
        await self._session.execute(query)
