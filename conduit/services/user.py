from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import (
    EmailAlreadyTakenException,
    IncorrectLoginInputException,
    UserNameAlreadyTakenException,
)
from conduit.domain.dtos.user import (
    CreateUserDTO,
    UpdatedUserDTO,
    UpdateUserDTO,
    UserDTO,
)
from conduit.domain.repositories.user import IUserRepository
from conduit.domain.services.user import IUserService


class UserService(IUserService):
    """Service to handle user get & update logic."""

    def __init__(self, user_repo: IUserRepository) -> None:
        self._user_repo = user_repo

    async def create_user(
        self, session: AsyncSession, user_to_create: CreateUserDTO
    ) -> UserDTO:
        if await self._user_repo.get_by_email(
            session=session, email=user_to_create.email
        ):
            raise EmailAlreadyTakenException()

        if await self._user_repo.get_by_username(
            session=session, username=user_to_create.username
        ):
            raise UserNameAlreadyTakenException()

        return await self._user_repo.create(session=session, create_item=user_to_create)

    async def get_user_by_id(self, session: AsyncSession, user_id: int) -> UserDTO:
        if not (
            user := await self._user_repo.get_by_id(session=session, user_id=user_id)
        ):
            raise IncorrectLoginInputException()
        return user

    async def get_user_by_email(self, session: AsyncSession, email: str) -> UserDTO:
        if not (
            user := await self._user_repo.get_by_email(session=session, email=email)
        ):
            raise IncorrectLoginInputException()
        return user

    async def get_user_by_username(
        self, session: AsyncSession, username: str
    ) -> UserDTO:
        if not (
            user := await self._user_repo.get_by_username(
                session=session, username=username
            )
        ):
            raise IncorrectLoginInputException()
        return user

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
        return UpdatedUserDTO(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            bio=updated_user.bio,
            image=updated_user.image_url,
        )
