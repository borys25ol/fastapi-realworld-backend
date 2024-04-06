from datetime import datetime, timedelta

import jwt
from structlog import get_logger

from conduit.core.exceptions import IncorrectJWTTokenException
from conduit.domain.dtos.jwt import AuthTokenDTO, JWTUserDTO
from conduit.domain.dtos.user import UserDTO
from conduit.domain.services.jwt import IJWTTokenService

logger = get_logger()


class JWTTokenService(IJWTTokenService):
    """Service to handle JWT tokens."""

    def __init__(
        self, secret_key: str, token_expiration_minutes: int, algorithm: str
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._token_expiration_minutes = token_expiration_minutes

    def generate_token(self, user: UserDTO) -> AuthTokenDTO:
        expire = datetime.now() + timedelta(minutes=self._token_expiration_minutes)
        payload = {"user_id": user.id, "username": user.username, "exp": expire}
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return AuthTokenDTO(token=token)

    def get_user_info_from_token(self, token_dto: AuthTokenDTO) -> JWTUserDTO:
        try:
            payload = jwt.decode(
                token_dto.token, self._secret_key, algorithms=[self._algorithm]
            )
        except jwt.InvalidTokenError as err:
            logger.error("Invalid JWT token", token=token_dto.token, error=err)
            raise IncorrectJWTTokenException()

        return JWTUserDTO(user_id=payload["user_id"], username=payload["user_id"])
