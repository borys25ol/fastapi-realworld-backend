import abc
from collections.abc import Collection, Mapping
from typing import Any

from conduit.domain.dtos.user import CreateUserDTO, UpdateUserDTO, UserDTO


class IUserRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def add(self, session: Any, create_item: CreateUserDTO) -> UserDTO: ...

    @abc.abstractmethod
    async def get_or_none(self, session: Any, user_id: int) -> UserDTO | None: ...

    @abc.abstractmethod
    async def get(self, session: Any, user_id: int) -> UserDTO: ...

    @abc.abstractmethod
    async def get_by_email_or_none(
        self, session: Any, email: str
    ) -> UserDTO | None: ...

    @abc.abstractmethod
    async def get_by_email(self, session: Any, email: str) -> UserDTO: ...

    @abc.abstractmethod
    async def list_by_users(
        self, session: Any, user_ids: Collection[int]
    ) -> list[UserDTO]: ...

    @abc.abstractmethod
    async def get_by_username_or_none(
        self, session: Any, username: str
    ) -> UserDTO | None: ...

    @abc.abstractmethod
    async def get_by_username(self, session: Any, username: str) -> UserDTO: ...

    @abc.abstractmethod
    async def update(
        self, session: Any, user_id: int, update_item: UpdateUserDTO
    ) -> UserDTO: ...
