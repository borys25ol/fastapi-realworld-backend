import abc
from collections.abc import Collection

from conduit.application.dtos.user import (
    CreateUserDTO,
    UpdatedUserDTO,
    UpdateUserDTO,
    UserDTO,
)
from conduit.domain.uow import IUnitOfWork


class IUserService(abc.ABC):
    @abc.abstractmethod
    async def create_user(
        self, uow: IUnitOfWork, user_to_create: CreateUserDTO
    ) -> UserDTO: ...

    @abc.abstractmethod
    async def get_user_by_id(self, uow: IUnitOfWork, user_id: int) -> UserDTO: ...

    @abc.abstractmethod
    async def get_user_by_email(self, uow: IUnitOfWork, email: str) -> UserDTO: ...

    @abc.abstractmethod
    async def get_user_by_username(
        self, uow: IUnitOfWork, username: str
    ) -> UserDTO: ...

    @abc.abstractmethod
    async def get_users_by_ids(
        self, uow: IUnitOfWork, user_ids: Collection[int]
    ) -> list[UserDTO]: ...

    @abc.abstractmethod
    async def update_user(
        self, uow: IUnitOfWork, current_user: UserDTO, user_to_update: UpdateUserDTO
    ) -> UpdatedUserDTO: ...
