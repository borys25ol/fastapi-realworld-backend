import abc
from typing import Any


class IFavoriteRepository(abc.ABC):
    """Favorite articles repository interface."""

    @abc.abstractmethod
    async def exists(self, session: Any, author_id: int, article_id: int) -> bool: ...

    @abc.abstractmethod
    async def count(self, session: Any, article_id: int) -> int: ...

    @abc.abstractmethod
    async def create(self, session: Any, article_id: int, user_id: int) -> None: ...

    @abc.abstractmethod
    async def delete(self, session: Any, article_id: int, user_id: int) -> None: ...
