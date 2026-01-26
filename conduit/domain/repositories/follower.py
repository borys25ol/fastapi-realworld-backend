import abc


class IFollowerRepository(abc.ABC):
    """Follower repository interface."""

    @abc.abstractmethod
    async def exists(self, follower_id: int, following_id: int) -> bool: ...

    @abc.abstractmethod
    async def list(self, follower_id: int, following_ids: list[int]) -> list[int]: ...

    @abc.abstractmethod
    async def create(self, follower_id: int, following_id: int) -> None: ...

    @abc.abstractmethod
    async def delete(self, follower_id: int, following_id: int) -> None: ...
