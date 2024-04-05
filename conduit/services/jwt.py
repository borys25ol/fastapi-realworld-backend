from datetime import datetime, timedelta

import jwt
from structlog import get_logger

from conduit.domain.dtos.jwt import AuthTokenDTO
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
        payload = {"user_id": user.id, "exp": expire}
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)
        return AuthTokenDTO(token=token)

    def get_user_id(self, token_dto: AuthTokenDTO) -> int | None:
        try:
            payload = jwt.decode(
                token_dto.token, self._secret_key, algorithms=[self._algorithm]
            )
        except jwt.InvalidTokenError as err:
            logger.info("Invalid JWT token", token=token_dto.token, error=err)
            return None
        user_id = payload["user_id"]
        return user_id
