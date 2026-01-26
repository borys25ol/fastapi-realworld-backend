import datetime

import pytest

from conduit.core.exceptions import ArticlePermissionException
from conduit.domain.entities.article import Article


def test_article_assert_owner_raises() -> None:
    article = Article(
        id=1,
        author_id=1,
        slug="title-123",
        title="Title",
        description="desc",
        body="body",
        created_at=datetime.datetime.now(),
    )
    with pytest.raises(ArticlePermissionException):
        article.assert_owner(user_id=2)


def test_article_update_content_updates_slug() -> None:
    article = Article(
        id=1,
        author_id=1,
        slug="title-123",
        title="Title",
        description="desc",
        body="body",
        created_at=datetime.datetime.now(),
    )
    article.update_content(title="New Title")
    assert article.title == "New Title"
    assert article.slug.startswith("new-title-")
