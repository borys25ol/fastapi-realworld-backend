import abc
from typing import Any

from conduit.domain.dtos.user import UpdatedUserDTO, UpdateUserDTO, UserDTO


class IUserService(abc.ABC):

    @abc.abstractmethod
    async def get_current_user(self, session: Any, token: str) -> UserDTO: ...

    @abc.abstractmethod
    async def update_user(
        self, session: Any, current_user: UserDTO, user_to_update: UpdateUserDTO
    ) -> UpdatedUserDTO: ...
