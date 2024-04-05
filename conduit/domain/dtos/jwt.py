from dataclasses import dataclass


@dataclass(frozen=True)
class AuthTokenDTO:
    token: str
