import abc
from typing import Any

from conduit.domain.dtos.profile import ProfileDTO
from conduit.domain.dtos.user import UserDTO


class IProfileService(abc.ABC):

    @abc.abstractmethod
    async def get_profile_by_username(
        self, session: Any, username: str, current_user: UserDTO | None = None
    ) -> ProfileDTO: ...

    @abc.abstractmethod
    async def get_profile_by_user_id(
        self, session: Any, user_id: int, current_user: UserDTO | None = None
    ) -> ProfileDTO: ...

    @abc.abstractmethod
    async def get_profiles_by_user_ids(
        self, session: Any, user_ids: list[int], current_user: UserDTO | None
    ) -> list[ProfileDTO]: ...

    @abc.abstractmethod
    async def follow_user(
        self, session: Any, username: str, current_user: UserDTO
    ) -> None: ...

    @abc.abstractmethod
    async def unfollow_user(
        self, session: Any, username: str, current_user: UserDTO
    ) -> None: ...
