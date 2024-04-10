import abc
from typing import Any

from conduit.domain.dtos.article import (
    ArticlesFeedDTO,
    ArticleWithExtraDTO,
    CreateArticleDTO,
)


class IArticleService(abc.ABC):

    @abc.abstractmethod
    async def create_new_article(
        self, session: Any, author_id: int, article_to_create: CreateArticleDTO
    ) -> ArticleWithExtraDTO: ...

    @abc.abstractmethod
    async def get_article_by_slug(
        self, session: Any, slug: str, user_id: int | None = None
    ) -> ArticleWithExtraDTO: ...

    @abc.abstractmethod
    async def get_articles_by_following_authors(
        self, session: Any, author_ids: list[int], user_id: int
    ) -> ArticlesFeedDTO: ...
