from collections.abc import Collection
from datetime import datetime

from conduit.core.exceptions import UserCreateException
from conduit.domain.dtos.user import (
    CreateUserDTO,
    CreateUserRecordDTO,
    UpdatedUserDTO,
    UpdateUserDTO,
    UpdateUserRecordDTO,
    UserDTO,
)
from conduit.domain.entities.user import User
from conduit.domain.services.user import IUserService
from conduit.domain.uow import IUnitOfWork
from conduit.services.password import get_password_hash


class UserService(IUserService):
    """Service to handle user get & update logic."""

    async def create_user(
        self, uow: IUnitOfWork, user_to_create: CreateUserDTO
    ) -> UserDTO:
        user = User(
            id=0,
            username=user_to_create.username,
            email=user_to_create.email,
            password_hash="",
            bio="",
            image_url=None,
            created_at=datetime.now(),
        )
        user.ensure_unique_email(
            exists=await uow.users.get_by_email_or_none(email=user_to_create.email)
            is not None
        )

        user.ensure_unique_username(
            exists=await uow.users.get_by_username_or_none(
                username=user_to_create.username
            )
            is not None
        )

        create_user_record = CreateUserRecordDTO(
            username=user_to_create.username,
            email=user_to_create.email,
            password_hash=get_password_hash(user_to_create.password),
        )
        try:
            user = await uow.users.add(create_item=create_user_record)
        except Exception as exc:
            raise UserCreateException() from exc
        return self._to_user_dto(user)

    async def get_user_by_id(self, uow: IUnitOfWork, user_id: int) -> UserDTO:
        user = await uow.users.get(user_id=user_id)
        return self._to_user_dto(user)

    async def get_user_by_email(self, uow: IUnitOfWork, email: str) -> UserDTO:
        user = await uow.users.get_by_email(email=email)
        return self._to_user_dto(user)

    async def get_user_by_username(self, uow: IUnitOfWork, username: str) -> UserDTO:
        user = await uow.users.get_by_username(username=username)
        return self._to_user_dto(user)

    async def get_users_by_ids(
        self, uow: IUnitOfWork, user_ids: Collection[int]
    ) -> list[UserDTO]:
        users = await uow.users.list_by_users(user_ids=user_ids)
        return [self._to_user_dto(user) for user in users]

    async def update_user(
        self, uow: IUnitOfWork, current_user: UserDTO, user_to_update: UpdateUserDTO
    ) -> UpdatedUserDTO:
        user = User(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            password_hash=current_user.password_hash,
            bio=current_user.bio,
            image_url=current_user.image_url,
            created_at=current_user.created_at,
        )
        if user_to_update.username and user_to_update.username != current_user.username:
            user.ensure_unique_username(
                exists=await uow.users.get_by_username_or_none(
                    username=user_to_update.username
                )
                is not None
            )

        if user_to_update.email and user_to_update.email != current_user.email:
            user.ensure_unique_email(
                exists=await uow.users.get_by_email_or_none(email=user_to_update.email)
                is not None
            )

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
            image=updated_user.image_url or "",
        )

    @staticmethod
    def _to_user_dto(user: User) -> UserDTO:
        dto = UserDTO(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            bio=user.bio,
            image_url=user.image_url or "",
            created_at=user.created_at,
        )
        dto.id = user.id
        return dto
