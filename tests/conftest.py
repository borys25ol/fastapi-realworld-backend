import contextlib
import os
from datetime import datetime
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import URL, text, create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from conduit.app import create_app
from conduit.core.config import get_app_settings
from conduit.core.container import Container
from conduit.core.dependencies import IArticleService, IJWTTokenService
from conduit.core.settings.base import BaseAppSettings
from conduit.domain.dtos.article import ArticleDTO, CreateArticleDTO
from conduit.domain.dtos.jwt import AuthTokenDTO
from conduit.domain.dtos.user import CreateUserDTO, UserDTO
from conduit.domain.repositories.user import IUserRepository
from conduit.infrastructure.models import Base

CREATE_TEST_DB_QUERY = "CREATE DATABASE {db_name}"


@pytest.fixture(autouse=True)
def check_app_env_mode_enabled():
    assert os.getenv("APP_ENV") == "test"


@pytest.fixture(scope="session")
def settings() -> BaseAppSettings:
    return get_app_settings()


@pytest.fixture(scope="session")
def create_test_db(settings: BaseAppSettings) -> None:
    url = URL.create(
        drivername="postgresql",
        username=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        database="postgres",
    )
    engine = create_engine(url=url, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        with contextlib.suppress(ProgrammingError):
            query = text(CREATE_TEST_DB_QUERY.format(db_name=settings.postgres_db))
            connection.execute(statement=query)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables(settings: BaseAppSettings, create_test_db) -> None:
    async_engine = create_async_engine(
        url=settings.sql_db_uri, isolation_level="AUTOCOMMIT"
    )
    async with async_engine.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)
        yield
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def test_client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        app=app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def di_container(settings: BaseAppSettings) -> Container:
    return Container(settings=settings)


@pytest_asyncio.fixture
async def session(di_container: Container) -> AsyncIterator[AsyncSession]:
    async with di_container.context_session() as session:
        yield session


@pytest.fixture
def user_to_create() -> CreateUserDTO:
    return CreateUserDTO(username="test", email="test@gmail.com", password="password")


@pytest.fixture
def article_to_create() -> CreateArticleDTO:
    return CreateArticleDTO(
        title="Test Article",
        description="Test Description",
        body="Test Body",
        tags=["tag1", "tag2"],
    )


@pytest.fixture
def not_exists_user() -> UserDTO:
    dto = UserDTO(
        username="username",
        email="email",
        password_hash="hash",
        bio="bio",
        image_url="link",
        created_at=datetime.now(),
    )
    dto.id = 9999
    return dto


@pytest.fixture
def user_repository(di_container: Container) -> IUserRepository:
    return di_container.user_repository()


@pytest.fixture
def article_service(di_container: Container) -> IArticleService:
    return di_container.article_service()


@pytest.fixture
def jwt_service(di_container: Container) -> IJWTTokenService:
    return di_container.jwt_service()


@pytest_asyncio.fixture
async def test_user(
    session: AsyncSession,
    user_repository: IUserRepository,
    user_to_create: CreateUserDTO,
) -> UserDTO:
    return await user_repository.create(session=session, create_item=user_to_create)


@pytest_asyncio.fixture
async def test_article(
    session: AsyncSession,
    article_service: IArticleService,
    article_to_create: CreateArticleDTO,
    test_user: UserDTO,
) -> ArticleDTO:
    return await article_service.create_new_article(
        session=session, author_id=test_user.id, article_to_create=article_to_create
    )


@pytest_asyncio.fixture
async def token_dto(jwt_service: IJWTTokenService, test_user: UserDTO) -> AuthTokenDTO:
    return jwt_service.generate_token(user=test_user)


@pytest_asyncio.fixture
async def not_exists_token_dto(
    jwt_service: IJWTTokenService, not_exists_user: UserDTO
) -> AuthTokenDTO:
    return jwt_service.generate_token(user=not_exists_user)


@pytest.fixture
def authorized_test_client(
    test_client: AsyncClient, token_dto: AuthTokenDTO
) -> AsyncClient:
    test_client.headers = {
        "Authorization": f"Token {token_dto.token}",
        **test_client.headers,
    }
    return test_client
