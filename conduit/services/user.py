from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import (
    EmailAlreadyTakenException,
    IncorrectLoginInputException,
    UserNameAlreadyTakenException,
)
from conduit.domain.dtos.user import UpdatedUserDTO, UpdateUserDTO, UserDTO
from conduit.domain.repositories.user import IUserRepository
from conduit.domain.services.auth_token import IAuthTokenService
from conduit.domain.services.user import IUserService


class UserService(IUserService):
    """Service to handle user get & update logic."""

    def __init__(
        self, user_repo: IUserRepository, auth_token_service: IAuthTokenService
    ) -> None:
        self._user_repo = user_repo
        self._auth_token_service = auth_token_service

    async def get_current_user(self, session: AsyncSession, token: str) -> UserDTO:
        jwt_user = self._auth_token_service.parse_jwt_token(token=token)
        current_user = await self._user_repo.get_by_id(
            session=session, user_id=jwt_user.user_id
        )
        if not current_user:
            raise IncorrectLoginInputException()

        return current_user

    async def update_user(
        self,
        session: AsyncSession,
        current_user: UserDTO,
        user_to_update: UpdateUserDTO,
    ) -> UpdatedUserDTO:
        if user_to_update.username and user_to_update.username != current_user.username:
            if await self._user_repo.get_by_username(
                session=session, username=user_to_update.username
            ):
                raise UserNameAlreadyTakenException()

        if user_to_update.email and user_to_update.email != current_user.email:
            if await self._user_repo.get_by_email(
                session=session, email=user_to_update.email
            ):
                raise EmailAlreadyTakenException()

        updated_user = await self._user_repo.update(
            session=session, user_id=current_user.id, update_item=user_to_update
        )
        jwt_token = self._auth_token_service.generate_jwt_token(user=updated_user)
        return UpdatedUserDTO(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            bio=updated_user.bio,
            image=updated_user.image_url,
            token=jwt_token,
        )
