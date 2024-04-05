import abc

from conduit.domain.dtos.jwt import AuthTokenDTO
from conduit.domain.dtos.user import UserDTO


class IJWTTokenService(abc.ABC):

    @abc.abstractmethod
    def generate_token(self, user: UserDTO) -> AuthTokenDTO: ...

    @abc.abstractmethod
    def get_user_id(self, token_dto: AuthTokenDTO) -> int | None: ...
