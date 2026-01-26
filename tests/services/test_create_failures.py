import datetime
from types import TracebackType
from typing import cast

import pytest

from conduit.application.dtos.article import CreateArticleDTO
from conduit.application.dtos.comment import CreateCommentDTO
from conduit.application.dtos.profile import ProfileDTO
from conduit.application.dtos.user import CreateUserDTO, UserDTO
from conduit.application.services.profile import IProfileService
from conduit.core.exceptions import (
    ArticleCreateException,
    CommentCreateException,
    UserCreateException,
)
from conduit.domain.entities.article import Article
from conduit.domain.entities.comment import Comment
from conduit.domain.entities.user import User
from conduit.domain.repositories.article import IArticleRepository
from conduit.domain.repositories.article_tag import IArticleTagRepository
from conduit.domain.repositories.comment import ICommentRepository
from conduit.domain.repositories.favorite import IFavoriteRepository
from conduit.domain.repositories.follower import IFollowerRepository
from conduit.domain.repositories.tag import ITagRepository
from conduit.domain.repositories.user import IUserRepository
from conduit.domain.uow import IUnitOfWork
from conduit.services.article import ArticleService
from conduit.services.comment import CommentService
from conduit.services.user import UserService


class _FailingArticleRepo:
    async def add(self, *_: object, **__: object) -> Article:
        raise RuntimeError("fail")


class _FailingUserRepo:
    async def get_by_email_or_none(self, *_: object, **__: object) -> User | None:
        return None

    async def get_by_username_or_none(self, *_: object, **__: object) -> User | None:
        return None

    async def add(self, *_: object, **__: object) -> User:
        raise RuntimeError("fail")


class _FailingCommentRepo:
    async def add(self, *_: object, **__: object) -> Comment:
        raise RuntimeError("fail")


class _ArticleRepo:
    async def get_by_slug(self, *_: object, **__: object) -> Article:
        return Article(
            id=1,
            author_id=1,
            slug="article-slug",
            title="title",
            description="description",
            body="body",
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now(),
        )


class _NoopArticleTagRepo:
    async def add_many(self, *_: object, **__: object) -> list[object]:
        return []


class _NoopFavoriteRepo:
    async def count(self, *_: object, **__: object) -> int:
        return 0

    async def exists(self, *_: object, **__: object) -> bool:
        return False


class _NoopProfileService(IProfileService):
    async def get_profile_by_username(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO | None = None
    ) -> ProfileDTO:
        raise AssertionError("Not expected to be called")

    async def get_profile_by_user_id(
        self, uow: IUnitOfWork, user_id: int, current_user: UserDTO | None = None
    ) -> ProfileDTO:
        raise AssertionError("Not expected to be called")

    async def get_profiles_by_user_ids(
        self, uow: IUnitOfWork, user_ids: list[int], current_user: UserDTO | None
    ) -> list[ProfileDTO]:
        raise AssertionError("Not expected to be called")

    async def follow_user(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO
    ) -> None:
        raise AssertionError("Not expected to be called")

    async def unfollow_user(
        self, uow: IUnitOfWork, username: str, current_user: UserDTO
    ) -> None:
        raise AssertionError("Not expected to be called")


class _MissingRepo:
    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"Missing repo dependency: {name}")


class _FakeUnitOfWork(IUnitOfWork):
    def __init__(
        self,
        users: IUserRepository | None = None,
        articles: IArticleRepository | None = None,
        article_tags: IArticleTagRepository | None = None,
        favorites: IFavoriteRepository | None = None,
        comments: ICommentRepository | None = None,
        followers: IFollowerRepository | None = None,
        tags: ITagRepository | None = None,
    ) -> None:
        missing_repo = _MissingRepo()
        self.users = cast(IUserRepository, users or missing_repo)
        self.articles = cast(IArticleRepository, articles or missing_repo)
        self.article_tags = cast(IArticleTagRepository, article_tags or missing_repo)
        self.favorites = cast(IFavoriteRepository, favorites or missing_repo)
        self.comments = cast(ICommentRepository, comments or missing_repo)
        self.followers = cast(IFollowerRepository, followers or missing_repo)
        self.tags = cast(ITagRepository, tags or missing_repo)

    async def __aenter__(self) -> "_FakeUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


@pytest.mark.anyio
async def test_article_create_raises_create_exception() -> None:
    service = ArticleService(profile_service=_NoopProfileService())
    uow = _FakeUnitOfWork(
        articles=cast(IArticleRepository, _FailingArticleRepo()),
        article_tags=cast(IArticleTagRepository, _NoopArticleTagRepo()),
        favorites=cast(IFavoriteRepository, _NoopFavoriteRepo()),
    )
    create_article_dto = CreateArticleDTO(
        title="title", description="desc", body="body", tags=[]
    )
    with pytest.raises(ArticleCreateException):
        await service.create_new_article(
            uow=uow, author_id=1, article_to_create=create_article_dto
        )


@pytest.mark.anyio
async def test_user_create_raises_create_exception() -> None:
    service = UserService()
    uow = _FakeUnitOfWork(users=cast(IUserRepository, _FailingUserRepo()))
    create_user_dto = CreateUserDTO(
        username="user", email="user@example.com", password="secret"
    )
    with pytest.raises(UserCreateException):
        await service.create_user(uow=uow, user_to_create=create_user_dto)


@pytest.mark.anyio
async def test_comment_create_raises_create_exception() -> None:
    current_user = UserDTO(
        username="user",
        email="user@example.com",
        password_hash="hash",
        bio="",
        image_url="",
        created_at=datetime.datetime.now(),
    )
    current_user.id = 1
    service = CommentService(profile_service=_NoopProfileService())
    uow = _FakeUnitOfWork(
        articles=cast(IArticleRepository, _ArticleRepo()),
        comments=cast(ICommentRepository, _FailingCommentRepo()),
    )
    with pytest.raises(CommentCreateException):
        await service.create_article_comment(
            uow=uow,
            slug="article-slug",
            comment_to_create=CreateCommentDTO(body="body"),
            current_user=current_user,
        )
