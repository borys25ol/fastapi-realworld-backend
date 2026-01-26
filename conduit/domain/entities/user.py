"""Domain entity for users."""

from dataclasses import dataclass
from datetime import datetime

from conduit.core.exceptions import (
    EmailAlreadyTakenException,
    UserNameAlreadyTakenException,
)


@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    bio: str
    image_url: str | None
    created_at: datetime
    updated_at: datetime | None = None

    def change_username(self, username: str) -> None:
        self._validate_username(username)
        self.username = username

    def change_email(self, email: str) -> None:
        self._validate_email(email)
        self.email = email

    def change_password_hash(self, password_hash: str) -> None:
        if not password_hash:
            raise ValueError("Invalid password hash")
        self.password_hash = password_hash

    def update_profile(
        self, bio: str | None = None, image_url: str | None = None
    ) -> None:
        if bio is not None:
            self.bio = bio
        if image_url is not None:
            self.image_url = image_url

    def ensure_unique_email(self, exists: bool) -> None:
        if exists:
            raise EmailAlreadyTakenException()

    def ensure_unique_username(self, exists: bool) -> None:
        if exists:
            raise UserNameAlreadyTakenException()

    @staticmethod
    def _validate_email(value: str) -> None:
        if not value or "@" not in value:
            raise ValueError("Invalid email")

    @staticmethod
    def _validate_username(value: str) -> None:
        if not value or len(value.strip()) < 3:
            raise ValueError("Invalid username")
