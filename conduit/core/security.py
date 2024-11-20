from typing import Any

from fastapi.security import APIKeyHeader
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN


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
