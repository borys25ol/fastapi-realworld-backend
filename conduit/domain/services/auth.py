import abc
from typing import Any

from conduit.domain.dtos.user import (
    CreatedUserDTO,
    CreateUserDTO,
    LoggedInUserDTO,
    LoginUserDTO,
)


class IUserAuthService(abc.ABC):

    @abc.abstractmethod
    async def sign_up_user(
        self, session: Any, user_to_create: CreateUserDTO
    ) -> CreatedUserDTO: ...

    @abc.abstractmethod
    async def sign_in_user(
        self, session: Any, user_to_login: LoginUserDTO
    ) -> LoggedInUserDTO: ...
