import datetime

import pytest

from conduit.core.exceptions import CommentPermissionException
from conduit.domain.entities.comment import Comment


def test_comment_assert_owner_raises() -> None:
    comment = Comment(
        id=1, body="body", author_id=1, article_id=1, created_at=datetime.datetime.now()
    )
    with pytest.raises(CommentPermissionException):
        comment.assert_owner(user_id=2)
