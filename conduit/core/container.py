import contextlib
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from conduit.core.config import get_app_settings
from conduit.core.settings.base import AppEnvTypes, BaseAppSettings
from conduit.domain.mapper import IModelMapper
from conduit.domain.repositories.user import IUserRepository
from conduit.infrastructure.mappers.user import UserModelMapper
from conduit.infrastructure.repositories.user import UserRepository


class Container:
    """Dependency injector project container."""

    def __init__(self, settings: BaseAppSettings) -> None:
        self._settings = settings
        self._engine = create_async_engine(
            url=settings.sql_db_uri,
            echo=self._settings.app_env != AppEnvTypes.production,
        )
        self._session = async_sessionmaker(bind=self._engine)

    @contextlib.asynccontextmanager
    async def db_session(self) -> AsyncIterator[AsyncSession]:
        session = self._session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @staticmethod
    def user_model_mapper() -> IModelMapper:
        return UserModelMapper()

    def user_repository(self) -> IUserRepository:
        return UserRepository(user_mapper=self.user_model_mapper())


container = Container(settings=get_app_settings())
