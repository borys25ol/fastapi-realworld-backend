from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from conduit.core.exceptions import (
    OwnProfileFollowingException,
    ProfileAlreadyFollowedException,
    ProfileNotFollowedFollowedException,
    ProfileNotFoundException,
    UserNotFoundException,
)
from conduit.domain.dtos.profile import ProfileDTO
from conduit.domain.dtos.user import UserDTO
from conduit.domain.repositories.follower import IFollowerRepository
from conduit.domain.services.profile import IProfileService
from conduit.domain.services.user import IUserService

logger = get_logger()


class ProfileService(IProfileService):
    """Service to handle user profiles and following logic."""

    def __init__(self, user_service: IUserService, follower_repo: IFollowerRepository):
        self._user_service = user_service
        self._follower_repo = follower_repo

    async def get_profile_by_username(
        self, session: AsyncSession, username: str, current_user: UserDTO | None = None
    ) -> ProfileDTO:
        try:
            target_user = await self._user_service.get_user_by_username(
                session=session, username=username
            )
        except UserNotFoundException:
            logger.exception("Profile not found", username=username)
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
        target_user = await self._user_service.get_user_by_id(
            session=session, user_id=user_id
        )
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

    async def get_profiles_by_user_ids(
        self, session: AsyncSession, user_ids: list[int], current_user: UserDTO | None
    ) -> list[ProfileDTO]:
        target_users = await self._user_service.get_users_by_ids(
            session=session, user_ids=user_ids
        )
        following_user_ids = (
            await self._follower_repo.list(
                session=session,
                follower_id=current_user.id,
                following_ids=[user.id for user in target_users],
            )
            if current_user
            else []
        )
        return [
            ProfileDTO(
                user_id=user_dto.id,
                username=user_dto.username,
                bio=user_dto.bio,
                image=user_dto.image_url,
                following=user_dto.id in following_user_ids,
            )
            for user_dto in target_users
        ]

    async def follow_user(
        self, session: AsyncSession, username: str, current_user: UserDTO
    ) -> None:
        if username == current_user.username:
            raise OwnProfileFollowingException()

        target_user = await self._user_service.get_user_by_username(
            session=session, username=username
        )
        if await self._follower_repo.exists(
            session, follower_id=current_user.id, following_id=target_user.id
        ):
            raise ProfileAlreadyFollowedException()

        await self._follower_repo.create(
            session=session, follower_id=current_user.id, following_id=target_user.id
        )

    async def unfollow_user(
        self, session: AsyncSession, username: str, current_user: UserDTO
    ) -> None:
        if username == current_user.username:
            raise OwnProfileFollowingException()

        target_user = await self._user_service.get_user_by_username(
            session=session, username=username
        )
        if not await self._follower_repo.exists(
            session, follower_id=current_user.id, following_id=target_user.id
        ):
            logger.exception("User not followed", username=username)
            raise ProfileNotFollowedFollowedException()

        await self._follower_repo.delete(
            session=session, follower_id=current_user.id, following_id=target_user.id
        )
