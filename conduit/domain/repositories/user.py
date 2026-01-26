import abc
from collections.abc import Collection

from conduit.domain.dtos.user import CreateUserRecordDTO, UpdateUserRecordDTO
from conduit.domain.entities.user import User


class IUserRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def add(self, create_item: CreateUserRecordDTO) -> User: ...

    @abc.abstractmethod
    async def get_or_none(self, user_id: int) -> User | None: ...

    @abc.abstractmethod
    async def get(self, user_id: int) -> User: ...

    @abc.abstractmethod
    async def get_by_email_or_none(self, email: str) -> User | None: ...

    @abc.abstractmethod
    async def get_by_email(self, email: str) -> User: ...

    @abc.abstractmethod
    async def list_by_users(self, user_ids: Collection[int]) -> list[User]: ...

    @abc.abstractmethod
    async def get_by_username_or_none(self, username: str) -> User | None: ...

    @abc.abstractmethod
    async def get_by_username(self, username: str) -> User: ...

    @abc.abstractmethod
    async def update(self, user_id: int, update_item: UpdateUserRecordDTO) -> User: ...
