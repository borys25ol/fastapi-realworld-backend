from typing import Annotated

from fastapi import Depends, Query

from conduit.api.schemas.requests.article import ArticlesFilters, ArticlesPagination
from conduit.core.providers import (
    get_article_service,
    get_auth_token_service,
    get_comment_service,
    get_profile_service,
    get_tag_service,
    get_uow,
    get_user_auth_service,
    get_user_service,
)
from conduit.core.security import HTTPTokenHeader
from conduit.domain.dtos.user import UserDTO
from conduit.domain.uow import IUnitOfWork
from conduit.services.article import ArticleService
from conduit.services.auth import UserAuthService
from conduit.services.auth_token import AuthTokenService
from conduit.services.comment import CommentService
from conduit.services.profile import ProfileService
from conduit.services.tag import TagService
from conduit.services.user import UserService

token_security = HTTPTokenHeader(
    name="Authorization",
    scheme_name="JWT Token",
    description="Token Format: `Token xxxxxx.yyyyyyy.zzzzzz`",
    raise_error=True,
)
token_security_optional = HTTPTokenHeader(
    name="Authorization",
    scheme_name="JWT Token",
    description="Token Format: `Token xxxxxx.yyyyyyy.zzzzzz`",
    raise_error=False,
)

JWTToken = Annotated[str, Depends(token_security)]
JWTTokenOptional = Annotated[str, Depends(token_security_optional)]

UnitOfWork = Annotated[IUnitOfWork, Depends(get_uow)]

IAuthTokenService = Annotated[AuthTokenService, Depends(get_auth_token_service)]
IUserAuthService = Annotated[UserAuthService, Depends(get_user_auth_service)]
IUserService = Annotated[UserService, Depends(get_user_service)]
IProfileService = Annotated[ProfileService, Depends(get_profile_service)]
ITagService = Annotated[TagService, Depends(get_tag_service)]
IArticleService = Annotated[ArticleService, Depends(get_article_service)]
ICommentService = Annotated[CommentService, Depends(get_comment_service)]

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


def get_articles_pagination(
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> ArticlesPagination:
    limit = min(limit, DEFAULT_ARTICLES_LIMIT)
    return ArticlesPagination(limit=limit, offset=offset)


def get_articles_filters(
    tag: str | None = None, author: str | None = None, favorited: str | None = None
) -> ArticlesFilters:
    return ArticlesFilters(tag=tag, author=author, favorited=favorited)


async def get_current_user_or_none(
    token: JWTTokenOptional,
    uow: UnitOfWork,
    auth_token_service: IAuthTokenService,
    user_service: IUserService,
) -> UserDTO | None:
    if token is None:
        return None
    jwt_user = auth_token_service.parse_jwt_token(token=token)
    current_user_dto = await user_service.get_user_by_id(
        uow=uow, user_id=jwt_user.user_id
    )
    return current_user_dto


async def get_current_user(
    token: JWTToken,
    uow: UnitOfWork,
    auth_token_service: IAuthTokenService,
    user_service: IUserService,
) -> UserDTO:
    jwt_user = auth_token_service.parse_jwt_token(token=token)
    current_user_dto = await user_service.get_user_by_id(
        uow=uow, user_id=jwt_user.user_id
    )
    return current_user_dto


Pagination = Annotated[ArticlesPagination, Depends(get_articles_pagination)]
QueryFilters = Annotated[ArticlesFilters, Depends(get_articles_filters)]
CurrentOptionalUser = Annotated[UserDTO | None, Depends(get_current_user_or_none)]
CurrentUser = Annotated[UserDTO, Depends(get_current_user)]
