import abc

from conduit.domain.dtos.user import (
    CreatedUserDTO,
    CreateUserDTO,
    LoggedInUserDTO,
    LoginUserDTO,
)
from conduit.domain.uow import IUnitOfWork


class IUserAuthService(abc.ABC):
    @abc.abstractmethod
    async def sign_up_user(
        self, uow: IUnitOfWork, user_to_create: CreateUserDTO
    ) -> CreatedUserDTO: ...

    @abc.abstractmethod
    async def sign_in_user(
        self, uow: IUnitOfWork, user_to_login: LoginUserDTO
    ) -> LoggedInUserDTO: ...
