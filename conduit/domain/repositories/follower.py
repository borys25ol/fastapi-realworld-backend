import abc
from typing import Any


class IFollowerRepository(abc.ABC):
    """Follower repository interface."""

    @abc.abstractmethod
    async def get(
        self, session: Any, follower_id: int, following_id: int
    ) -> int | None: ...

    @abc.abstractmethod
    async def create(
        self, session: Any, follower_id: int, following_id: int
    ) -> None: ...

    @abc.abstractmethod
    async def delete(
        self, session: Any, follower_id: int, following_id: int
    ) -> None: ...
