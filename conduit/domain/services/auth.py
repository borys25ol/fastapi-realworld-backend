import abc
from typing import Any

from conduit.domain.dtos.user import (
    CreatedUserDTO,
    CreateUserDTO,
    LoggedInUserDTO,
    LoginUserDTO,
    UpdatedUserDTO,
    UpdateUserDTO,
    UserDTO,
)


class IUserAuthService(abc.ABC):

    @abc.abstractmethod
    async def get_current_user(self, session: Any, token: str) -> UserDTO: ...

    @abc.abstractmethod
    async def sign_up_user(
        self, session: Any, user_to_create: CreateUserDTO
    ) -> CreatedUserDTO: ...

    @abc.abstractmethod
    async def sign_in_user(
        self, session: Any, user_to_login: LoginUserDTO
    ) -> LoggedInUserDTO: ...

    @abc.abstractmethod
    async def update_user(
        self, session: Any, current_user: UserDTO, user_to_update: UpdateUserDTO
    ) -> UpdatedUserDTO: ...
