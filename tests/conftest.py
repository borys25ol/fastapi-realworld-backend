import os
from collections.abc import Generator
from datetime import datetime
from typing import TypeAlias

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_utils import create_database, database_exists, drop_database

from conduit.app import create_app
from conduit.core.config import get_app_settings
from conduit.core.container import Container
from conduit.core.dependencies import IArticleService, IAuthTokenService
from conduit.core.settings.base import BaseAppSettings
from conduit.dtos.domain.article import ArticleDTO, CreateArticleDTO
from conduit.dtos.domain.user import CreateUserDTO, UserDTO
from conduit.infrastructure.models import Base
from conduit.interfaces.repositories.article import IArticleRepository
from conduit.interfaces.repositories.user import IUserRepository
from conduit.interfaces.services.user import IUserService

SetupFixture: TypeAlias = None


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def check_app_env_mode_enabled() -> None:
    assert os.getenv("APP_ENV") == "test"


@pytest.fixture(scope="session")
def create_test_db(settings: BaseAppSettings) -> Generator[None, None, None]:
    test_db_sql_uri = settings.sql_db_uri.set(drivername="postgresql")

    if database_exists(url=test_db_sql_uri):
        drop_database(url=test_db_sql_uri)

    create_database(url=test_db_sql_uri)
    yield

    drop_database(url=test_db_sql_uri)


@pytest.fixture(autouse=True)
def create_tables(settings: BaseAppSettings) -> Generator[None, None, None]:
    engine = create_engine(
        url=settings.sql_db_uri.set(drivername="postgresql"),
        isolation_level="AUTOCOMMIT",
    )
    Base.metadata.create_all(bind=engine)
    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def _raise_rate_limit_for_tests() -> Generator[None, None, None]:
    # The in-memory rate limiter accumulates across the session-scoped app.
    # Raise the ceiling so functional tests never hit 429 — the rate-limiter
    # bug itself is documented separately in test_bug_probes.py and the README.
    from conduit.api.middlewares import RateLimitingMiddleware
    original = RateLimitingMiddleware.rate_limit_requests
    RateLimitingMiddleware.rate_limit_requests = 100_000
    yield
    RateLimitingMiddleware.rate_limit_requests = original


@pytest.fixture(scope="session")
def application(create_test_db: SetupFixture) -> FastAPI:
    return create_app()


@pytest.fixture(scope="session")
def settings() -> BaseAppSettings:
    return get_app_settings()


@pytest.fixture(scope="session")
def di_container(settings: BaseAppSettings) -> Container:
    return Container(settings=settings)


@pytest.fixture
async def session(di_container: Container) -> AsyncSession:
    async with di_container.context_session() as session:
        yield session


@pytest.fixture
def user_repository(di_container: Container) -> IUserRepository:
    return di_container.user_repository()


@pytest.fixture
def article_repository(di_container: Container) -> IArticleRepository:
    return di_container.article_repository()


@pytest.fixture
def article_service(di_container: Container) -> IArticleService:
    return di_container.article_service()


@pytest.fixture
def auth_token_service(di_container: Container) -> IAuthTokenService:
    return di_container.auth_token_service()


@pytest.fixture
def user_service(di_container: Container) -> IUserService:
    return di_container.user_service()


@pytest.fixture
def user_to_create() -> CreateUserDTO:
    return CreateUserDTO(username="test", email="test@gmail.com", password="password")


@pytest.fixture
def article_to_create() -> CreateArticleDTO:
    return CreateArticleDTO(
        title="Test Article",
        description="Test Description",
        body="Test Body Content",
        tags=["tag1", "tag2"],
    )


@pytest.fixture
def not_exists_user() -> UserDTO:
    return UserDTO(
        id=9999,
        username="username",
        email="email",
        password_hash="hash",
        bio="bio",
        image="link",
        created_at=datetime.now(),
    )


@pytest.fixture
async def test_user(
    session: AsyncSession, user_service: IUserService, user_to_create: CreateUserDTO
) -> UserDTO:
    return await user_service.create_user(
        session=session, user_to_create=user_to_create
    )


@pytest.fixture
async def test_article(
    session: AsyncSession,
    article_service: IArticleService,
    article_to_create: CreateArticleDTO,
    test_user: UserDTO,
) -> ArticleDTO:
    return await article_service.create_new_article(
        session=session, author_id=test_user.id, article_to_create=article_to_create
    )


@pytest.fixture
async def jwt_token(auth_token_service: IAuthTokenService, test_user: UserDTO) -> str:
    return auth_token_service.generate_jwt_token(user=test_user)


@pytest.fixture
async def not_exists_jwt_token(
    auth_token_service: IAuthTokenService, not_exists_user: UserDTO
) -> str:
    return auth_token_service.generate_jwt_token(user=not_exists_user)


@pytest.fixture
async def test_client(application: FastAPI) -> AsyncClient:
    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
async def authorized_test_client(application: FastAPI, jwt_token: str) -> AsyncClient:
    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers={
            "Authorization": f"Token {jwt_token}",
            "Content-Type": "application/json",
        },
    ) as client:
        yield client
