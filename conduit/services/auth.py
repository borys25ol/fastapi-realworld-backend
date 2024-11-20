from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import IncorrectLoginInputException
from conduit.core.security import verify_password
from conduit.core.utils.errors import get_or_raise
from conduit.domain.dtos.user import (
    CreatedUserDTO,
    CreateUserDTO,
    LoggedInUserDTO,
    LoginUserDTO,
)
from conduit.domain.services.auth import IUserAuthService
from conduit.domain.services.auth_token import IAuthTokenService
from conduit.domain.services.user import IUserService


class UserAuthService(IUserAuthService):
    """Service to handle users auth logic."""

    def __init__(
        self, user_service: IUserService, auth_token_service: IAuthTokenService
    ):
        self._user_service = user_service
        self._auth_token_service = auth_token_service

    async def sign_up_user(
        self, session: AsyncSession, user_to_create: CreateUserDTO
    ) -> CreatedUserDTO:
        user = await self._user_service.create_user(
            session=session, user_to_create=user_to_create
        )
        jwt_token = self._auth_token_service.generate_jwt_token(user=user)
        return CreatedUserDTO(
            id=user.id,
            email=user.email,
            username=user.username,
            bio=user.bio,
            image=user.image_url,
            token=jwt_token,
        )

    async def sign_in_user(
        self, session: AsyncSession, user_to_login: LoginUserDTO
    ) -> LoggedInUserDTO:
        user = await self._user_service.get_user_by_email(
            session=session, email=user_to_login.email
        )
        if not verify_password(
            plain_password=user_to_login.password, hashed_password=user.password_hash
        ):
            raise IncorrectLoginInputException()

        jwt_token = self._auth_token_service.generate_jwt_token(user=user)
        return LoggedInUserDTO(
            email=user.email,
            username=user.username,
            bio=user.bio,
            image=user.image_url,
            token=jwt_token,
        )
