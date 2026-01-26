"""Domain entity for comments."""

from dataclasses import dataclass
from datetime import datetime

from conduit.core.exceptions import CommentPermissionException


@dataclass
class Comment:
    id: int
    body: str
    author_id: int
    article_id: int
    created_at: datetime
    updated_at: datetime | None = None

    def can_delete(self, user_id: int) -> bool:
        return self.author_id == user_id

    def assert_owner(self, user_id: int) -> None:
        if not self.can_delete(user_id=user_id):
            raise CommentPermissionException()
