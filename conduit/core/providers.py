from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache

from conduit.core.config import get_app_settings
from conduit.core.container import container
from conduit.domain.services.article import IArticleService
from conduit.domain.services.auth import IUserAuthService
from conduit.domain.services.auth_token import IAuthTokenService
from conduit.domain.services.comment import ICommentService
from conduit.domain.services.profile import IProfileService
from conduit.domain.services.tag import ITagService
from conduit.domain.services.user import IUserService
from conduit.domain.uow import IUnitOfWork
from conduit.services.article import ArticleService
from conduit.services.auth import UserAuthService
from conduit.services.auth_token import AuthTokenService
from conduit.services.comment import CommentService
from conduit.services.profile import ProfileService
from conduit.services.tag import TagService
from conduit.services.user import UserService


async def get_uow() -> AsyncIterator[IUnitOfWork]:
    uow = container.unit_of_work()
    async with uow:
        yield uow


@lru_cache
def get_auth_token_service() -> IAuthTokenService:
    settings = get_app_settings()
    return AuthTokenService(
        secret_key=settings.jwt_secret_key,
        token_expiration_minutes=settings.jwt_token_expiration_minutes,
        algorithm=settings.jwt_algorithm,
    )


@lru_cache
def get_user_service() -> IUserService:
    return UserService()


@lru_cache
def get_profile_service() -> IProfileService:
    return ProfileService(user_service=get_user_service())


@lru_cache
def get_user_auth_service() -> IUserAuthService:
    return UserAuthService(
        user_service=get_user_service(), auth_token_service=get_auth_token_service()
    )


@lru_cache
def get_tag_service() -> ITagService:
    return TagService()


@lru_cache
def get_article_service() -> IArticleService:
    return ArticleService(profile_service=get_profile_service())


@lru_cache
def get_comment_service() -> ICommentService:
    return CommentService(profile_service=get_profile_service())
