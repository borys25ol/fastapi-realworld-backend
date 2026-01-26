from dataclasses import dataclass


@dataclass
class ProfileDTO:
    user_id: int
    username: str
    bio: str = ""
    image: str | None = None
    following: bool = False
