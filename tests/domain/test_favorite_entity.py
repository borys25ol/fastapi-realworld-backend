import datetime

import pytest

from conduit.core.exceptions import (
    ArticleAlreadyFavoritedException,
    ArticleNotFavoritedException,
)
from conduit.domain.entities.favorite import Favorite


def test_favorite_assert_not_favorited_raises() -> None:
    favorite = Favorite(user_id=1, article_id=1, created_at=datetime.datetime.now())
    with pytest.raises(ArticleAlreadyFavoritedException):
        favorite.assert_not_favorited(is_favorited=True)


def test_favorite_assert_favorited_raises() -> None:
    favorite = Favorite(user_id=1, article_id=1, created_at=datetime.datetime.now())
    with pytest.raises(ArticleNotFavoritedException):
        favorite.assert_favorited(is_favorited=False)
