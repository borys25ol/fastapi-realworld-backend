from typing import Any

import pytest
from fastapi import FastAPI

from conduit.core.utils.errors import get_or_raise


@pytest.fixture(scope="session", autouse=True)
def create_test_db() -> None:
    return


@pytest.fixture(scope="session", autouse=True)
def create_tables() -> None:
    return


class TestException(Exception):
    pass


async def mock_awaitable(result: Any) -> Any:
    return result


@pytest.mark.anyio
async def test_get_or_raise_returns_value(application: FastAPI) -> None:
    result = await get_or_raise(mock_awaitable("expected_value"), TestException())
    assert result == "expected_value"


@pytest.mark.anyio
async def test_get_or_raise_raises_exception(application: FastAPI) -> None:
    with pytest.raises(TestException):
        await get_or_raise(mock_awaitable(None), TestException())


@pytest.mark.anyio
async def test_get_or_raise_raises_custom_exception_message(
    application: FastAPI,
) -> None:
    with pytest.raises(TestException, match="Custom error message"):
        await get_or_raise(mock_awaitable(None), TestException("Custom error message"))
