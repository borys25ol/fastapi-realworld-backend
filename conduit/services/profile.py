from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import (
    OwnProfileFollowingException,
    ProfileNotFoundException,
)
from conduit.domain.dtos.profile import ProfileDTO
from conduit.domain.dtos.user import UserDTO
from conduit.domain.repositories.follower import IFollowerRepository
from conduit.domain.repositories.user import IUserRepository
from conduit.domain.services.profile import IProfileService


class ProfileService(IProfileService):
    """Service to handle user profiles and following logic."""

    def __init__(self, user_repo: IUserRepository, follower_repo: IFollowerRepository):
        self._user_repo = user_repo
        self._follower_repo = follower_repo

    async def get_profile_by_username(
        self, session: AsyncSession, username: str, current_user: UserDTO | None = None
    ) -> ProfileDTO:
        target_user = await self._user_repo.get_by_username(
            session=session, username=username
        )
        if not target_user:
            raise ProfileNotFoundException()

        profile = ProfileDTO(
            user_id=target_user.id,
            username=target_user.username,
            bio=target_user.bio,
            image=target_user.image_url,
        )
        if current_user:
            profile.following = await self._follower_repo.exists(
                session=session,
                follower_id=current_user.id,
                following_id=target_user.id,
            )
        return profile

    async def get_profile_by_user_id(
        self, session: AsyncSession, user_id: int, current_user: UserDTO | None = None
    ) -> ProfileDTO:
        target_user = await self._user_repo.get_by_id(session=session, user_id=user_id)
        if not target_user:
            raise ProfileNotFoundException()

        profile = ProfileDTO(
            user_id=target_user.id,
            username=target_user.username,
            bio=target_user.bio,
            image=target_user.image_url,
        )
        if current_user:
            profile.following = await self._follower_repo.exists(
                session=session,
                follower_id=current_user.id,
                following_id=target_user.id,
            )
        return profile

    async def get_following_profiles(
        self, session: AsyncSession, current_user: UserDTO
    ) -> list[ProfileDTO]:
        following_user_ids = await self._follower_repo.get(
            session=session, follower_id=current_user.id
        )
        following_users = await self._user_repo.get_by_ids(
            session=session, ids=following_user_ids
        )
        return [
            ProfileDTO(
                user_id=user_dto.id,
                username=user_dto.username,
                bio=user_dto.bio,
                image=user_dto.image_url,
                following=True,
            )
            for user_dto in following_users
        ]

    async def add_user_into_followers(
        self, session: AsyncSession, username: str, current_user: UserDTO
    ) -> None:
        if username == current_user.username:
            raise OwnProfileFollowingException()

        target_user = await self._user_repo.get_by_username(
            session=session, username=username
        )
        if not target_user:
            raise ProfileNotFoundException()

        await self._follower_repo.create(
            session=session, follower_id=current_user.id, following_id=target_user.id
        )

    async def remove_user_from_followers(
        self, session: AsyncSession, username: str, current_user: UserDTO
    ) -> None:
        if username == current_user.username:
            raise OwnProfileFollowingException()

        target_user = await self._user_repo.get_by_username(
            session=session, username=username
        )
        if not target_user:
            raise ProfileNotFoundException()

        await self._follower_repo.delete(
            session=session, follower_id=current_user.id, following_id=target_user.id
        )
