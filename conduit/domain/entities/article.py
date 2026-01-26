"""Domain entity for articles."""

from dataclasses import dataclass
from datetime import datetime

from conduit.core.exceptions import ArticlePermissionException
from conduit.core.utils.slug import make_slug_from_title


@dataclass
class Article:
    id: int
    author_id: int
    slug: str
    title: str
    description: str
    body: str
    created_at: datetime
    updated_at: datetime | None = None

    def can_modify(self, user_id: int) -> bool:
        return self.author_id == user_id

    def assert_owner(self, user_id: int) -> None:
        if not self.can_modify(user_id=user_id):
            raise ArticlePermissionException()

    def update_content(
        self,
        title: str | None = None,
        description: str | None = None,
        body: str | None = None,
    ) -> None:
        if title is not None:
            self.title = title
            self.slug = make_slug_from_title(title=title)
            self._validate_slug(self.slug)
        if description is not None:
            self.description = description
        if body is not None:
            self.body = body

    @staticmethod
    def _validate_slug(value: str) -> None:
        if not value or " " in value:
            raise ValueError("Invalid slug")
