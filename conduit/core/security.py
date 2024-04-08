from typing import Any

from fastapi.security import APIKeyHeader
from passlib.context import CryptContext
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HTTPTokenHeader(APIKeyHeader):

    def __init__(self, raise_error: bool, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.raise_error = raise_error

    async def __call__(self, request: Request) -> str | None:
        api_key = request.headers.get(self.model.name)
        if not api_key:
            if not self.raise_error:
                return ""
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Missing authorization credentials",
            )

        try:
            token_prefix, token = api_key.split(" ")
        except ValueError:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Invalid token schema"
            )

        if token_prefix.lower() != "token":
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, detail="Invalid token schema"
            )

        return token


def get_password_hash(password: str) -> str:
    """
    Convert user password to hash string.
    """
    return pwd_context.hash(secret=password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check if the user password from request is valid.
    """
    return pwd_context.verify(secret=plain_password, hash=hashed_password)
