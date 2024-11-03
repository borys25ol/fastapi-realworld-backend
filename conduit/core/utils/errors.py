from collections.abc import Awaitable
from typing import Any


async def get_or_raise(awaitable: Awaitable, exception: Exception) -> Any:
    """
    Await the awaitable and raise the given exception if the result is None.
    """
    result = await awaitable
    if not result:
        raise exception
    return result
