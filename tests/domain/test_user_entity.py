import datetime

import pytest

from conduit.core.exceptions import (
    EmailAlreadyTakenException,
    UserNameAlreadyTakenException,
)
from conduit.domain.entities.user import User


def test_user_ensure_unique_email_raises() -> None:
    user = User(
        id=1,
        username="user",
        email="user@example.com",
        password_hash="hash",
        bio="",
        image_url=None,
        created_at=datetime.datetime.now(),
    )
    with pytest.raises(EmailAlreadyTakenException):
        user.ensure_unique_email(exists=True)


def test_user_ensure_unique_username_raises() -> None:
    user = User(
        id=1,
        username="user",
        email="user@example.com",
        password_hash="hash",
        bio="",
        image_url=None,
        created_at=datetime.datetime.now(),
    )
    with pytest.raises(UserNameAlreadyTakenException):
        user.ensure_unique_username(exists=True)


@pytest.mark.parametrize("invalid_email", ["", "invalid"])
def test_user_change_email_validates(invalid_email: str) -> None:
    user = User(
        id=1,
        username="user",
        email="user@example.com",
        password_hash="hash",
        bio="",
        image_url=None,
        created_at=datetime.datetime.now(),
    )
    with pytest.raises(ValueError):
        user.change_email(invalid_email)


@pytest.mark.parametrize("invalid_username", ["", "  ", "ab"])
def test_user_change_username_validates(invalid_username: str) -> None:
    user = User(
        id=1,
        username="user",
        email="user@example.com",
        password_hash="hash",
        bio="",
        image_url=None,
        created_at=datetime.datetime.now(),
    )
    with pytest.raises(ValueError):
        user.change_username(invalid_username)
