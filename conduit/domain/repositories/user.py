import abc
from collections.abc import Collection, Mapping
from typing import Any

from conduit.domain.dtos.user import CreateUserDTO, UpdateUserDTO, UserDTO


class IUserRepository(abc.ABC):
    """User repository interface."""

    @abc.abstractmethod
    async def create(self, session: Any, create_item: CreateUserDTO) -> UserDTO: ...

    @abc.abstractmethod
    async def get_by_email(self, session: Any, email: str) -> UserDTO | None: ...

    @abc.abstractmethod
    async def get_by_id(self, session: Any, user_id: int) -> UserDTO: ...

    @abc.abstractmethod
    async def get_all_by_ids(
        self, session: Any, ids: Collection[int]
    ) -> list[UserDTO]: ...

    @abc.abstractmethod
    async def get_by_username(self, session: Any, username: str) -> UserDTO | None: ...

    @abc.abstractmethod
    async def update(
        self, session: Any, user_id: int, update_item: UpdateUserDTO
    ) -> UserDTO: ...
