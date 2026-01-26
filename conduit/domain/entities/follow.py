"""Domain entity for follows."""

from dataclasses import dataclass
from datetime import datetime

from conduit.core.exceptions import (
    OwnProfileFollowingException,
    ProfileAlreadyFollowedException,
    ProfileNotFollowedFollowedException,
)


@dataclass
class Follow:
    follower_id: int
    following_id: int
    created_at: datetime

    def is_self_follow(self) -> bool:
        return self.follower_id == self.following_id

    def assert_not_self(self) -> None:
        if self.is_self_follow():
            raise OwnProfileFollowingException()

    def assert_not_already_followed(self, is_followed: bool) -> None:
        if is_followed:
            raise ProfileAlreadyFollowedException()

    def assert_followed(self, is_followed: bool) -> None:
        if not is_followed:
            raise ProfileNotFollowedFollowedException()
