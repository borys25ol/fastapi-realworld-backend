from fastapi.security import APIKeyHeader
from fastapi.security.utils import get_authorization_scheme_param
from passlib.context import CryptContext
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class HTTPTokenHeader(APIKeyHeader):

    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get(self.model.name)
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Missing authorization credentials",
            )
        return credentials


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
