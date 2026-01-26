import abc


class IFavoriteRepository(abc.ABC):
    """Favorite articles repository interface."""

    @abc.abstractmethod
    async def exists(self, author_id: int, article_id: int) -> bool: ...

    @abc.abstractmethod
    async def count(self, article_id: int) -> int: ...

    @abc.abstractmethod
    async def create(self, article_id: int, user_id: int) -> None: ...

    @abc.abstractmethod
    async def delete(self, article_id: int, user_id: int) -> None: ...
