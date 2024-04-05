"""
Module with project dependencies.
"""

from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.core.container import container
from conduit.services.auth import UserAuthService
from conduit.services.jwt import JWTTokenService

token_security = APIKeyHeader(name="Authorization")

JWTToken = Annotated[str, Depends(token_security)]
DBSession = Annotated[AsyncSession, Depends(container.session)]
IJWTTokenService = Annotated[JWTTokenService, Depends(container.jwt_service)]
IUserAuthService = Annotated[UserAuthService, Depends(container.user_auth_service)]
