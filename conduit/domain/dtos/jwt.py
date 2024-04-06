from dataclasses import dataclass


@dataclass(frozen=True)
class AuthTokenDTO:
    token: str


@dataclass(frozen=True)
class JWTUserDTO:
    user_id: int
    username: str
