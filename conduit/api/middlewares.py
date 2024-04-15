from datetime import datetime, timedelta
from typing import Any, Unpack

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from conduit.core.exceptions import RateLimitExceededException


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that handle requests rate limiting.
    """

    rate_limit_duration = timedelta(minutes=1)
    rate_limit_requests = 100

    def __init__(self, *args: Unpack[tuple[Any]], **kwargs: Any):
        super().__init__(*args, **kwargs)
        # Dictionary to store request counts for each IP.
        self.request_counts: dict[str, tuple[int, datetime]] = {}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = request.client.host

        request_count, last_request = self.request_counts.get(
            client_ip, (0, datetime.min)
        )
        # Calculate the time elapsed since the last request
        elapsed_time = datetime.now() - last_request

        if elapsed_time > self.rate_limit_duration:
            request_count = 1
        else:
            if request_count >= self.rate_limit_requests:
                return RateLimitExceededException.get_response()
            request_count += 1

        self.request_counts[client_ip] = (request_count, datetime.now())

        response = await call_next(request)
        return response
