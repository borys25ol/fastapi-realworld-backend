import abc
from collections.abc import Collection

from conduit.domain.dtos.user import CreateUserRecordDTO, UpdateUserRecordDTO, UserDTO


class IUserRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def add(self, create_item: CreateUserRecordDTO) -> UserDTO: ...

    @abc.abstractmethod
    async def get_or_none(self, user_id: int) -> UserDTO | None: ...

    @abc.abstractmethod
    async def get(self, user_id: int) -> UserDTO: ...

    @abc.abstractmethod
    async def get_by_email_or_none(self, email: str) -> UserDTO | None: ...

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> UserDTO: ...

    @abc.abstractmethod
    async def list_by_users(self, user_ids: Collection[int]) -> list[UserDTO]: ...

    @abc.abstractmethod
    async def get_by_username_or_none(self, username: str) -> UserDTO | None: ...

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> UserDTO: ...

    @abc.abstractmethod
    async def update(
        self, user_id: int, update_item: UpdateUserRecordDTO
    ) -> UserDTO: ...
