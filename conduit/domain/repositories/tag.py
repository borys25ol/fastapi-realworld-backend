import abc

from conduit.domain.entities.tag import Tag


class ITagRepository(abc.ABC):
    @abc.abstractmethod
    async def list(self) -> list[Tag]: ...
