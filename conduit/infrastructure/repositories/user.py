from collections.abc import Collection
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.exceptions import UserNotFoundException
from conduit.domain.entities.user import User as UserEntity
from conduit.domain.repositories.user import IUserRepository
from conduit.infrastructure.mappers.user_mapper import model_to_entity
from conduit.infrastructure.models import User


class UserRepository(IUserRepository):
    """Repository for User model."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: UserEntity) -> UserEntity:
        query = (
            insert(User)
            .values(
                username=user.username,
                email=user.email,
                password_hash=user.password_hash,
                image_url=user.image_url or "",
                bio=user.bio,
                created_at=user.created_at,
            )
            .returning(User)
        )
        result = await self._session.execute(query)
        return model_to_entity(result.scalar_one())

    async def get_by_email_or_none(self, email: str) -> UserEntity | None:
        query = select(User).where(User.email == email)
        if user := await self._session.scalar(query):
            return model_to_entity(user)
        return None

    async def get_by_email(self, email: str) -> UserEntity:
        query = select(User).where(User.email == email)
        if not (user := await self._session.scalar(query)):
            raise UserNotFoundException()
        return model_to_entity(user)

    async def get_or_none(self, user_id: int) -> UserEntity | None:
        query = select(User).where(User.id == user_id)
        if user := await self._session.scalar(query):
            return model_to_entity(user)
        return None

    async def get(self, user_id: int) -> UserEntity:
        query = select(User).where(User.id == user_id)
        if not (user := await self._session.scalar(query)):
            raise UserNotFoundException()
        return model_to_entity(user)

    async def list_by_users(self, user_ids: Collection[int]) -> list[UserEntity]:
        query = select(User).where(User.id.in_(user_ids))
        users = await self._session.scalars(query)
        return [model_to_entity(user) for user in users]

    async def get_by_username_or_none(self, username: str) -> UserEntity | None:
        query = select(User).where(User.username == username)
        if user := await self._session.scalar(query):
            return model_to_entity(user)
        return None

    async def get_by_username(self, username: str) -> UserEntity:
        query = select(User).where(User.username == username)
        if not (user := await self._session.scalar(query)):
            raise UserNotFoundException()
        return model_to_entity(user)

    async def update(self, user: UserEntity) -> UserEntity:
        query = (
            update(User)
            .where(User.id == user.id)
            .values(updated_at=datetime.now())
            .returning(User)
        )
        query = query.values(
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            bio=user.bio,
            image_url=user.image_url or "",
        )

        result = await self._session.execute(query)
        return model_to_entity(result.scalar_one())
