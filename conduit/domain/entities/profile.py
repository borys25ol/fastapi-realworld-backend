"""Domain entity for profiles."""

from dataclasses import dataclass


@dataclass
class Profile:
    user_id: int
    username: str
    bio: str = ""
    image: str | None = None
    following: bool = False
