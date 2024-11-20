import abc
from typing import Any

from conduit.domain.dtos.user import (
    CreateUserDTO,
    UpdatedUserDTO,
    UpdateUserDTO,
    UserDTO,
)


class IUserService(abc.ABC):

    @abc.abstractmethod
    async def create_user(
        self, session: Any, user_to_create: CreateUserDTO
    ) -> UserDTO: ...

    @abc.abstractmethod
    async def get_user_by_id(self, session: Any, user_id: int) -> UserDTO: ...

    @abc.abstractmethod
    async def get_user_by_email(self, session: Any, email: str) -> UserDTO: ...

    @abc.abstractmethod
    async def get_user_by_username(self, session: Any, username: str) -> UserDTO: ...

    @abc.abstractmethod
    async def update_user(
        self, session: Any, current_user: UserDTO, user_to_update: UpdateUserDTO
    ) -> UpdatedUserDTO: ...
