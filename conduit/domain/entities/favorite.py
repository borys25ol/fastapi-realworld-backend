"""Domain entity for favorites."""

from dataclasses import dataclass
from datetime import datetime

from conduit.core.exceptions import (
    ArticleAlreadyFavoritedException,
    ArticleNotFavoritedException,
)


@dataclass
class Favorite:
    user_id: int
    article_id: int
    created_at: datetime

    def assert_not_favorited(self, is_favorited: bool) -> None:
        if is_favorited:
            raise ArticleAlreadyFavoritedException()

    def assert_favorited(self, is_favorited: bool) -> None:
        if not is_favorited:
            raise ArticleNotFavoritedException()
