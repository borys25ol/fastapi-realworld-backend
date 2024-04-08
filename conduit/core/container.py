import contextlib
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from conduit.core.config import get_app_settings
from conduit.core.settings.base import AppEnvTypes, BaseAppSettings
from conduit.domain.mapper import IModelMapper
from conduit.domain.repositories.follower import IFollowerRepository
from conduit.domain.repositories.user import IUserRepository
from conduit.domain.services.auth import IUserAuthService
from conduit.domain.services.jwt import IJWTTokenService
from conduit.domain.services.profile import IProfileService
from conduit.infrastructure.mappers.user import UserModelMapper
from conduit.infrastructure.repositories.follower import FollowerRepository
from conduit.infrastructure.repositories.user import UserRepository
from conduit.services.auth import UserAuthService
from conduit.services.jwt import JWTTokenService
from conduit.services.profile import ProfileService


class Container:
    """Dependency injector project container."""

    def __init__(self, settings: BaseAppSettings) -> None:
        self._settings = settings
        self._engine = create_async_engine(
            url=settings.sql_db_uri,
            echo=self._settings.app_env != AppEnvTypes.production,
            isolation_level="AUTOCOMMIT",
        )
        self._session = async_sessionmaker(bind=self._engine)

    @contextlib.asynccontextmanager
    async def context_session(self) -> AsyncIterator[AsyncSession]:
        session = self._session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session() as session:
            try:
                yield session
            finally:
                await session.close()

    @staticmethod
    def user_model_mapper() -> IModelMapper:
        return UserModelMapper()

    def user_repository(self) -> IUserRepository:
        return UserRepository(user_mapper=self.user_model_mapper())

    @staticmethod
    def follower_repository() -> IFollowerRepository:
        return FollowerRepository()

    def jwt_service(self) -> IJWTTokenService:
        return JWTTokenService(
            secret_key=self._settings.jwt_secret_key,
            token_expiration_minutes=self._settings.jwt_token_expiration_minutes,
            algorithm=self._settings.jwt_algorithm,
        )

    def user_auth_service(self) -> IUserAuthService:
        return UserAuthService(
            user_repo=self.user_repository(), jwt_service=self.jwt_service()
        )

    def profile_service(self) -> IProfileService:
        return ProfileService(
            user_repo=self.user_repository(), follower_repo=self.follower_repository()
        )


container = Container(settings=get_app_settings())
