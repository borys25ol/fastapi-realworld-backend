from datetime import datetime, timedelta

import jwt
from structlog import get_logger

from conduit.core.exceptions import IncorrectJWTTokenException
from conduit.domain.dtos.auth_token import TokenPayloadDTO
from conduit.domain.dtos.user import UserDTO
from conduit.domain.services.auth_token import IAuthTokenService

logger = get_logger()


class AuthTokenService(IAuthTokenService):
    """Service to handle JWT tokens."""

    def __init__(
        self, secret_key: str, token_expiration_minutes: int, algorithm: str
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._token_expiration_minutes = token_expiration_minutes

    def generate_jwt_token(self, user: UserDTO) -> str:
        expire = datetime.now() + timedelta(minutes=self._token_expiration_minutes)
        payload = {"user_id": user.id, "username": user.username, "exp": expire}
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def parse_jwt_token(self, token: str) -> TokenPayloadDTO:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.InvalidTokenError as err:
            logger.error("Invalid JWT token", token=token, error=err)
            raise IncorrectJWTTokenException()

        return TokenPayloadDTO(user_id=payload["user_id"], username=payload["username"])
