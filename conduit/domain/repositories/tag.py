import abc

from conduit.domain.dtos.tag import TagRecordDTO


class ITagRepository(abc.ABC):
    @abc.abstractmethod
    async def list(self) -> list[TagRecordDTO]: ...
