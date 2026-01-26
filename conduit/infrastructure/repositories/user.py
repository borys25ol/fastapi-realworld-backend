from collections.abc import Collection
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import UserNotFoundException
from conduit.domain.dtos.user import CreateUserRecordDTO, UpdateUserRecordDTO
from conduit.domain.entities.user import User as UserEntity
from conduit.domain.repositories.user import IUserRepository
from conduit.infrastructure.models import User


class UserRepository(IUserRepository):
    """Repository for User model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, create_item: CreateUserRecordDTO) -> UserEntity:
        query = (
            insert(User)
            .values(
                username=create_item.username,
                email=create_item.email,
                password_hash=create_item.password_hash,
                image_url="https://api.realworld.io/images/smiley-cyrus.jpeg",
                bio="",
                created_at=datetime.now(),
            )
            .returning(User)
        )
        result = await self._session.execute(query)
        return self._to_user_entity(result.scalar_one())

    async def get_by_email_or_none(self, email: str) -> UserEntity | None:
        query = select(User).where(User.email == email)
        if user := await self._session.scalar(query):
            return self._to_user_entity(user)
        return None

    async def get_by_email(self, email: str) -> UserEntity:
        query = select(User).where(User.email == email)
        if not (user := await self._session.scalar(query)):
            raise UserNotFoundException()
        return self._to_user_entity(user)

    async def get_or_none(self, user_id: int) -> UserEntity | None:
        query = select(User).where(User.id == user_id)
        if user := await self._session.scalar(query):
            return self._to_user_entity(user)
        return None

    async def get(self, user_id: int) -> UserEntity:
        query = select(User).where(User.id == user_id)
        if not (user := await self._session.scalar(query)):
            raise UserNotFoundException()
        return self._to_user_entity(user)

    async def list_by_users(self, user_ids: Collection[int]) -> list[UserEntity]:
        query = select(User).where(User.id.in_(user_ids))
        users = await self._session.scalars(query)
        return [self._to_user_entity(user) for user in users]

    async def get_by_username_or_none(self, username: str) -> UserEntity | None:
        query = select(User).where(User.username == username)
        if user := await self._session.scalar(query):
            return self._to_user_entity(user)
        return None

    async def get_by_username(self, username: str) -> UserEntity:
        query = select(User).where(User.username == username)
        if not (user := await self._session.scalar(query)):
            raise UserNotFoundException()
        return self._to_user_entity(user)

    async def update(
        self, user_id: int, update_item: UpdateUserRecordDTO
    ) -> UserEntity:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(updated_at=datetime.now())
            .returning(User)
        )
        if update_item.username is not None:
            query = query.values(username=update_item.username)
        if update_item.email is not None:
            query = query.values(email=update_item.email)
        if update_item.password_hash is not None:
            query = query.values(password_hash=update_item.password_hash)
        if update_item.bio is not None:
            query = query.values(bio=update_item.bio)
        if update_item.image_url is not None:
            query = query.values(image_url=update_item.image_url)

        result = await self._session.execute(query)
        return self._to_user_entity(result.scalar_one())

    @staticmethod
    def _to_user_entity(model: User) -> UserEntity:
        return UserEntity(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            bio=model.bio,
            image_url=model.image_url,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
