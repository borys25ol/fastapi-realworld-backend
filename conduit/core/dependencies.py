from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.api.schemas.requests.article import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    ArticlesFilters,
)
from conduit.core.container import container
from conduit.core.security import HTTPTokenHeader
from conduit.domain.dtos.user import UserDTO
from conduit.services.article import ArticleService
from conduit.services.auth import UserAuthService
from conduit.services.jwt import JWTTokenService
from conduit.services.profile import ProfileService
from conduit.services.tag import TagService

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

DBSession = Annotated[AsyncSession, Depends(container.session)]

IJWTTokenService = Annotated[JWTTokenService, Depends(container.jwt_service)]
IUserAuthService = Annotated[UserAuthService, Depends(container.user_auth_service)]
IProfileService = Annotated[ProfileService, Depends(container.profile_service)]
ITagService = Annotated[TagService, Depends(container.tag_service)]
IArticleService = Annotated[ArticleService, Depends(container.article_service)]


def get_articles_filters(
    tag: str | None = None,
    author: str | None = None,
    favorited: str | None = None,
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> ArticlesFilters:
    return ArticlesFilters(
        tag=tag, author=author, favorited=favorited, limit=limit, offset=offset
    )


async def get_current_user_or_none(
    token: JWTTokenOptional, session: DBSession, user_auth_service: IUserAuthService
) -> UserDTO | None:
    if token:
        current_user_dto = await user_auth_service.get_current_user(
            session=session, token=token
        )
        return current_user_dto


async def get_current_user(
    token: JWTToken, session: DBSession, user_auth_service: IUserAuthService
) -> UserDTO:
    current_user_dto = await user_auth_service.get_current_user(
        session=session, token=token
    )
    return current_user_dto


QueryFilters = Annotated[ArticlesFilters, Depends(get_articles_filters)]
CurrentOptionalUser = Annotated[UserDTO | None, Depends(get_current_user_or_none)]
CurrentUser = Annotated[UserDTO, Depends(get_current_user)]
