import abc

from conduit.domain.dtos.jwt import AuthTokenDTO, JWTUserDTO
from conduit.domain.dtos.user import UserDTO


class IJWTTokenService(abc.ABC):

    @abc.abstractmethod
    def generate_token(self, user: UserDTO) -> AuthTokenDTO: ...

    @abc.abstractmethod
    def get_user_info_from_token(self, auth_token: AuthTokenDTO) -> JWTUserDTO: ...
