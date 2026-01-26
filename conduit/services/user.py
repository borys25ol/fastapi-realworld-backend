from collections.abc import Collection

from conduit.core.exceptions import (
    EmailAlreadyTakenException,
    UserCreateException,
    UserNameAlreadyTakenException,
)
from conduit.domain.dtos.user import (
    CreateUserDTO,
    CreateUserRecordDTO,
    UpdatedUserDTO,
    UpdateUserDTO,
    UpdateUserRecordDTO,
    UserDTO,
)
from conduit.domain.services.user import IUserService
from conduit.domain.uow import IUnitOfWork
from conduit.services.password import get_password_hash


class UserService(IUserService):
    """Service to handle user get & update logic."""

    async def create_user(
        self, uow: IUnitOfWork, user_to_create: CreateUserDTO
    ) -> UserDTO:
        if await uow.users.get_by_email_or_none(email=user_to_create.email):
            raise EmailAlreadyTakenException()

        if await uow.users.get_by_username_or_none(username=user_to_create.username):
            raise UserNameAlreadyTakenException()

        create_user_record = CreateUserRecordDTO(
            username=user_to_create.username,
            email=user_to_create.email,
            password_hash=get_password_hash(user_to_create.password),
        )
        try:
            return await uow.users.add(create_item=create_user_record)
        except Exception as exc:
            raise UserCreateException() from exc

    async def get_user_by_id(self, uow: IUnitOfWork, user_id: int) -> UserDTO:
        return await uow.users.get(user_id=user_id)

    async def get_user_by_email(self, uow: IUnitOfWork, email: str) -> UserDTO:
        return await uow.users.get_by_email(email=email)

    async def get_user_by_username(self, uow: IUnitOfWork, username: str) -> UserDTO:
        return await uow.users.get_by_username(username=username)

    async def get_users_by_ids(
        self, uow: IUnitOfWork, user_ids: Collection[int]
    ) -> list[UserDTO]:
        return await uow.users.list_by_users(user_ids=user_ids)

    async def update_user(
        self, uow: IUnitOfWork, current_user: UserDTO, user_to_update: UpdateUserDTO
    ) -> UpdatedUserDTO:
        if user_to_update.username and user_to_update.username != current_user.username:
            if await uow.users.get_by_username_or_none(
                username=user_to_update.username
            ):
                raise UserNameAlreadyTakenException()

        if user_to_update.email and user_to_update.email != current_user.email:
            if await uow.users.get_by_email_or_none(email=user_to_update.email):
                raise EmailAlreadyTakenException()

        update_record = UpdateUserRecordDTO(
            username=user_to_update.username,
            email=user_to_update.email,
            password_hash=(
                get_password_hash(user_to_update.password)
                if user_to_update.password is not None
                else None
            ),
            bio=user_to_update.bio,
            image_url=user_to_update.image_url,
        )
        updated_user = await uow.users.update(
            user_id=current_user.id, update_item=update_record
        )
        return UpdatedUserDTO(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            bio=updated_user.bio,
            image=updated_user.image_url,
        )
