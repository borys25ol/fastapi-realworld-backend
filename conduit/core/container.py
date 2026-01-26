import contextlib
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from conduit.core.config import get_app_settings
from conduit.core.settings.base import BaseAppSettings
from conduit.domain.services.article import IArticleService
from conduit.domain.services.auth import IUserAuthService
from conduit.domain.services.auth_token import IAuthTokenService
from conduit.domain.services.comment import ICommentService
from conduit.domain.services.profile import IProfileService
from conduit.domain.services.tag import ITagService
from conduit.domain.services.user import IUserService
from conduit.domain.uow import IUnitOfWork
from conduit.infrastructure.uow import SqlAlchemyUnitOfWork
from conduit.services.article import ArticleService
from conduit.services.auth import UserAuthService
from conduit.services.auth_token import AuthTokenService
from conduit.services.comment import CommentService
from conduit.services.profile import ProfileService
from conduit.services.tag import TagService
from conduit.services.user import UserService


class Container:
    """Dependency injector project container."""

    def __init__(self, settings: BaseAppSettings) -> None:
        self._settings = settings
        self._engine = create_async_engine(**settings.sqlalchemy_engine_props)
        self._session = async_sessionmaker(bind=self._engine, expire_on_commit=False)

    @contextlib.asynccontextmanager
    async def context_session(self) -> AsyncIterator[AsyncSession]:
        session = self._session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self._session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    def auth_token_service(self) -> IAuthTokenService:
        return AuthTokenService(
            secret_key=self._settings.jwt_secret_key,
            token_expiration_minutes=self._settings.jwt_token_expiration_minutes,
            algorithm=self._settings.jwt_algorithm,
        )

    def unit_of_work(self) -> IUnitOfWork:
        return SqlAlchemyUnitOfWork(self._session)

    def user_auth_service(self) -> IUserAuthService:
        return UserAuthService(
            user_service=self.user_service(),
            auth_token_service=self.auth_token_service(),
        )

    def user_service(self) -> IUserService:
        return UserService()

    def profile_service(self) -> IProfileService:
        return ProfileService(user_service=self.user_service())

    def tag_service(self) -> ITagService:
        return TagService()

    def article_service(self) -> IArticleService:
        return ArticleService(profile_service=self.profile_service())

    def comment_service(self) -> ICommentService:
        return CommentService(profile_service=self.profile_service())


container = Container(settings=get_app_settings())
