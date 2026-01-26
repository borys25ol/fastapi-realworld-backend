import datetime

import pytest

from conduit.core.exceptions import (
    OwnProfileFollowingException,
    ProfileAlreadyFollowedException,
    ProfileNotFollowedFollowedException,
)
from conduit.domain.entities.follow import Follow


def test_follow_assert_not_self_raises() -> None:
    follow = Follow(follower_id=1, following_id=1, created_at=datetime.datetime.now())
    with pytest.raises(OwnProfileFollowingException):
        follow.assert_not_self()


def test_follow_assert_not_already_followed_raises() -> None:
    follow = Follow(follower_id=1, following_id=2, created_at=datetime.datetime.now())
    with pytest.raises(ProfileAlreadyFollowedException):
        follow.assert_not_already_followed(is_followed=True)


def test_follow_assert_followed_raises() -> None:
    follow = Follow(follower_id=1, following_id=2, created_at=datetime.datetime.now())
    with pytest.raises(ProfileNotFollowedFollowedException):
        follow.assert_followed(is_followed=False)
