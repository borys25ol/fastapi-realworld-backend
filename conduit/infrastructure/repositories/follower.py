from datetime import datetime

from sqlalchemy import delete, exists, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.repositories.follower import IFollowerRepository
from conduit.infrastructure.models import Follower


class FollowerRepository(IFollowerRepository):
    """Repository for Follower model."""

    async def exists(
        self, session: AsyncSession, follower_id: int, following_id: int
    ) -> bool:
        query = (
            exists()
            .where(
                Follower.follower_id == follower_id,
                Follower.following_id == following_id,
            )
            .select()
        )
        result = await session.execute(query)
        return result.scalar()

    async def get(self, session: AsyncSession, follower_id: int) -> list[int]:
        query = select(Follower.following_id).where(Follower.follower_id == follower_id)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
        self, session: AsyncSession, follower_id: int, following_id: int
    ) -> None:
        query = insert(Follower).values(
            follower_id=follower_id,
            following_id=following_id,
            created_at=datetime.now(),
        )
        await session.execute(query)

    async def delete(
        self, session: AsyncSession, follower_id: int, following_id: int
    ) -> None:
        query = delete(Follower).where(
            Follower.follower_id == follower_id, Follower.following_id == following_id
        )
        await session.execute(query)
