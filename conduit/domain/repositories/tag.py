import abc

from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.domain.dtos.tag import TagDTO


class ITagRepository(abc.ABC):

    @abc.abstractmethod
    async def create(self, session: AsyncSession, tags: list[str]) -> list[TagDTO]: ...

    @abc.abstractmethod
    async def get_all(self, session: AsyncSession) -> list[TagDTO]: ...
