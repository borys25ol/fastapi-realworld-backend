from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPayloadDTO:
    user_id: int
    username: str
