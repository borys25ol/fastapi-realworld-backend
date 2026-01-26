import abc

from conduit.application.dtos.profile import ProfileDTO
from conduit.application.dtos.user import UserDTO
from conduit.domain.uow import IUnitOfWork


class IProfileService(abc.ABC):
    @abc.abstractmethod
    async def get_profile_by_username(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO | None = None
    ) -> ProfileDTO: ...

    @abc.abstractmethod
    async def get_profile_by_user_id(
        self, uow: IUnitOfWork, user_id: int, current_user: UserDTO | None = None
    ) -> ProfileDTO: ...

    @abc.abstractmethod
    async def get_profiles_by_user_ids(
        self, uow: IUnitOfWork, user_ids: list[int], current_user: UserDTO | None
    ) -> list[ProfileDTO]: ...

    @abc.abstractmethod
    async def follow_user(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO
    ) -> None: ...

    @abc.abstractmethod
    async def unfollow_user(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO
    ) -> None: ...
