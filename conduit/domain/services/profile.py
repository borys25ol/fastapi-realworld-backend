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
    async def get_followed_profiles(
        self, session: Any, current_user: UserDTO
    ) -> dict[int, ProfileDTO]: ...

    @abc.abstractmethod
    async def add_user_into_followers(
        self, session: Any, username: str, current_user: UserDTO
    ) -> None: ...

    @abc.abstractmethod
    async def remove_user_from_followers(
        self, session: Any, username: str, current_user: UserDTO
    ) -> None: ...
