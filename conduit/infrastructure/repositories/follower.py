from datetime import datetime

from sqlalchemy import delete, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.repositories.follower import IFollowerRepository
from conduit.infrastructure.models import FollowerFollowingMap


class FollowerRepository(IFollowerRepository):
    """Follower repository interface."""

    async def get(
        self, session: AsyncSession, follower_id: int, following_id: int
    ) -> int | None:
        query = select(FollowerFollowingMap.following_id).where(
            FollowerFollowingMap.follower_id == follower_id,
            FollowerFollowingMap.following_id == following_id,
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self, session: AsyncSession, follower_id: int, following_id: int
    ) -> None:
        query = insert(FollowerFollowingMap).values(
            follower_id=follower_id,
            following_id=following_id,
            created_at=datetime.now(),
        )
        await session.execute(query)

    async def delete(
        self, session: AsyncSession, follower_id: int, following_id: int
    ) -> None:
        query = delete(FollowerFollowingMap).where(
            FollowerFollowingMap.follower_id == follower_id,
            FollowerFollowingMap.following_id == following_id,
        )
        await session.execute(query)
