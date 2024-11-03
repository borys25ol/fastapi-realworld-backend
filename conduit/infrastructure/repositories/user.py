from collections.abc import Collection, Mapping
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.security import get_password_hash
from conduit.domain.dtos.user import CreateUserDTO, UpdateUserDTO, UserDTO
from conduit.domain.mapper import IModelMapper
from conduit.domain.repositories.user import IUserRepository
from conduit.infrastructure.models import User


class UserRepository(IUserRepository):
    """Repository for User model."""

    def __init__(self, user_mapper: IModelMapper[User, UserDTO]):
        self._user_mapper = user_mapper

    async def create(
        self, session: AsyncSession, create_item: CreateUserDTO
    ) -> UserDTO:
        query = (
            insert(User)
            .values(
                username=create_item.username,
                email=create_item.email,
                password_hash=get_password_hash(create_item.password),
                image_url="https://api.realworld.io/images/smiley-cyrus.jpeg",
                bio="",
                created_at=datetime.now(),
            )
            .returning(User)
        )
        result = await session.execute(query)
        return self._user_mapper.to_dto(result.scalar())

    async def get_by_email(self, session: AsyncSession, email: str) -> UserDTO | None:
        query = select(User).where(User.email == email)
        if user := await session.scalar(query):
            return self._user_mapper.to_dto(user)

    async def get_by_id(self, session: AsyncSession, user_id: int) -> UserDTO | None:
        query = select(User).where(User.id == user_id)
        if user := await session.scalar(query):
            return self._user_mapper.to_dto(user)

    async def get_all_by_ids(
        self, session: AsyncSession, ids: Collection[int]
    ) -> list[UserDTO]:
        query = select(User).where(User.id.in_(ids))
        users = await session.scalars(query)
        return [self._user_mapper.to_dto(user) for user in users]

    async def get_by_username(
        self, session: AsyncSession, username: str
    ) -> UserDTO | None:
        query = select(User).where(User.username == username)
        if user := await session.scalar(query):
            return self._user_mapper.to_dto(user)

    async def update(
        self, session: AsyncSession, user_id: int, update_item: UpdateUserDTO
    ) -> UserDTO:
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
        if update_item.password is not None:
            query = query.values(password_hash=get_password_hash(update_item.password))
        if update_item.bio is not None:
            query = query.values(bio=update_item.bio)
        if update_item.image_url is not None:
            query = query.values(image_url=update_item.image_url)

        result = await session.execute(query)
        return self._user_mapper.to_dto(result.scalar())
