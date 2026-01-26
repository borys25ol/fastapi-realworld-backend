from datetime import datetime

from structlog import get_logger

from conduit.application.dtos.profile import ProfileDTO
from conduit.application.dtos.user import UserDTO
from conduit.application.mappers.profile_mapper import user_to_profile_dto
from conduit.application.services.profile import IProfileService
from conduit.application.services.user import IUserService
from conduit.core.exceptions import ProfileNotFoundException, UserNotFoundException
from conduit.domain.entities.follow import Follow
from conduit.domain.uow import IUnitOfWork

logger = get_logger()


class ProfileService(IProfileService):
    """Service to handle user profiles and following logic."""

    def __init__(self, user_service: IUserService):
        self._user_service = user_service

    async def get_profile_by_username(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO | None = None
    ) -> ProfileDTO:
        try:
            target_user = await self._user_service.get_user_by_username(
                uow=uow, username=username
            )
        except UserNotFoundException:
            logger.exception("Profile not found", username=username)
            raise ProfileNotFoundException()

        profile = user_to_profile_dto(user=target_user, following=False)
        if current_user:
            profile.following = await uow.followers.exists(
                follower_id=current_user.id, following_id=target_user.id
            )
        return profile

    async def get_profile_by_user_id(
        self, uow: IUnitOfWork, user_id: int, current_user: UserDTO | None = None
    ) -> ProfileDTO:
        target_user = await self._user_service.get_user_by_id(uow=uow, user_id=user_id)
        profile = user_to_profile_dto(user=target_user, following=False)
        if current_user:
            profile.following = await uow.followers.exists(
                follower_id=current_user.id, following_id=target_user.id
            )
        return profile

    async def get_profiles_by_user_ids(
        self, uow: IUnitOfWork, user_ids: list[int], current_user: UserDTO | None
    ) -> list[ProfileDTO]:
        target_users = await self._user_service.get_users_by_ids(
            uow=uow, user_ids=user_ids
        )
        following_user_ids = (
            await uow.followers.list(
                follower_id=current_user.id,
                following_ids=[user.id for user in target_users],
            )
            if current_user
            else []
        )
        return [
            user_to_profile_dto(
                user=user_dto, following=user_dto.id in following_user_ids
            )
            for user_dto in target_users
        ]

    async def follow_user(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO
    ) -> None:
        target_user = await self._user_service.get_user_by_username(
            uow=uow, username=username
        )
        follow = Follow(
            follower_id=current_user.id,
            following_id=target_user.id,
            created_at=datetime.now(),
        )
        follow.assert_not_self()
        follow.assert_not_already_followed(
            is_followed=await uow.followers.exists(
                follower_id=current_user.id, following_id=target_user.id
            )
        )

        await uow.followers.create(
            follower_id=current_user.id, following_id=target_user.id
        )

    async def unfollow_user(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO
    ) -> None:
        target_user = await self._user_service.get_user_by_username(
            uow=uow, username=username
        )
        follow = Follow(
            follower_id=current_user.id,
            following_id=target_user.id,
            created_at=datetime.now(),
        )
        is_followed = await uow.followers.exists(
            follower_id=current_user.id, following_id=target_user.id
        )
        if not is_followed:
            logger.exception("User not followed", username=username)
        follow.assert_followed(is_followed=is_followed)

        await uow.followers.delete(
            follower_id=current_user.id, following_id=target_user.id
        )
