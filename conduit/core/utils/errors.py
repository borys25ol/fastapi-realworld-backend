from collections import defaultdict
from collections.abc import Awaitable, Sequence
from typing import Any


async def get_or_raise(awaitable: Awaitable, exception: Exception) -> Any:
    """
    Await the awaitable and raise the given exception if the result is None.
    """
    result = await awaitable
    if not result:
        raise exception
    return result


def format_errors(errors: Sequence[Any]) -> dict[str, list[str]]:
    """
    Format errors from pydantic validation errors.
    """
    result: defaultdict[str, list[str]] = defaultdict(list)
    for error in errors:
        field = error["loc"][-1]
        message = error.get("ctx", {}).get("reason") or error["msg"]
        result[field].append(message.lower())
    return dict(result)
