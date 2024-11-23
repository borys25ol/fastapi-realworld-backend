import abc

from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.dtos.tag import TagDTO


class ITagRepository(abc.ABC):

    @abc.abstractmethod
    async def list(self, session: AsyncSession) -> list[TagDTO]: ...
