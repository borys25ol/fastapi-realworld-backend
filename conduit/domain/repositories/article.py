import abc

from conduit.domain.entities.article import Article


class IArticleRepository(abc.ABC):
    """Article repository interface."""

    @abc.abstractmethod
    async def add(self, article: Article) -> Article: ...

    @abc.abstractmethod
    async def get_by_slug_or_none(self, slug: str) -> Article | None: ...

    @abc.abstractmethod
    async def get_by_slug(self, slug: str) -> Article: ...

    @abc.abstractmethod
    async def delete_by_slug(self, slug: str) -> None: ...

    @abc.abstractmethod
    async def update_by_slug(self, slug: str, article: Article) -> Article: ...

    @abc.abstractmethod
    async def list_by_followings(
        self, user_id: int, limit: int, offset: int
    ) -> list: ...

    @abc.abstractmethod
    async def list_by_filters(
        self,
        user_id: int | None,
        limit: int,
        offset: int,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> list: ...

    @abc.abstractmethod
    async def count_by_followings(self, user_id: int) -> int: ...

    @abc.abstractmethod
    async def count_by_filters(
        self,
        tag: str | None = None,
        author: str | None = None,
        favorited: str | None = None,
    ) -> int: ...
