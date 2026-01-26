from structlog import get_logger

from conduit.application.dtos.user import (
    CreatedUserDTO,
    CreateUserDTO,
    LoggedInUserDTO,
    LoginUserDTO,
)
from conduit.application.mappers.user_mapper import (
    user_dto_to_created_user_dto,
    user_dto_to_logged_in_user_dto,
)
from conduit.application.services.auth import IUserAuthService
from conduit.application.services.auth_token import IAuthTokenService
from conduit.application.services.user import IUserService
from conduit.core.exceptions import IncorrectLoginInputException, UserNotFoundException
from conduit.domain.uow import IUnitOfWork
from conduit.services.password import verify_password

logger = get_logger()


class UserAuthService(IUserAuthService):
    """Service to handle users auth logic."""

    def __init__(
        self, user_service: IUserService, auth_token_service: IAuthTokenService
    ):
        self._user_service = user_service
        self._auth_token_service = auth_token_service

    async def sign_up_user(
        self, uow: IUnitOfWork, user_to_create: CreateUserDTO
    ) -> CreatedUserDTO:
        user = await self._user_service.create_user(
            uow=uow, user_to_create=user_to_create
        )
        jwt_token = self._auth_token_service.generate_jwt_token(user=user)
        return user_dto_to_created_user_dto(user=user, token=jwt_token)

    async def sign_in_user(
        self, uow: IUnitOfWork, user_to_login: LoginUserDTO
    ) -> LoggedInUserDTO:
        try:
            user = await self._user_service.get_user_by_email(
                uow=uow, email=user_to_login.email
            )
        except UserNotFoundException:
            logger.error("User not found", email=user_to_login.email)
            raise IncorrectLoginInputException()

        if not verify_password(
            plain_password=user_to_login.password, hashed_password=user.password_hash
        ):
            logger.error("Incorrect password", email=user_to_login.email)
            raise IncorrectLoginInputException()

        jwt_token = self._auth_token_service.generate_jwt_token(user=user)
        return user_dto_to_logged_in_user_dto(user=user, token=jwt_token)
