"""
Module with project dependencies.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.core.container import container
from conduit.core.security import HTTPTokenHeader
from conduit.services.auth import UserAuthService
from conduit.services.jwt import JWTTokenService

token_security = HTTPTokenHeader(
    name="Authorization",
    scheme_name="JWTToken",
    description="Token Format: `Token <JWT>`. Example: `Token 123456789`",
)

JWTToken = Annotated[str, Depends(token_security)]
DBSession = Annotated[AsyncSession, Depends(container.session)]
IJWTTokenService = Annotated[JWTTokenService, Depends(container.jwt_service)]
IUserAuthService = Annotated[UserAuthService, Depends(container.user_auth_service)]
