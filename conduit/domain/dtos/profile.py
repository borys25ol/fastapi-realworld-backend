from dataclasses import dataclass


@dataclass
class ProfileDTO:
    username: str
    bio: str = ""
    image: str | None = None
    following: bool = False
