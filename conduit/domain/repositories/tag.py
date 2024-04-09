import abc
from collections.abc import Sequence

from sqlmodel.ext.asyncio.session import AsyncSession

from conduit.domain.dtos.tag import CreateTagDTO, TagDTO


class ITagRepository(abc.ABC):

    @abc.abstractmethod
    async def create(
        self, session: AsyncSession, tags: Sequence[CreateTagDTO]
    ) -> None: ...

    @abc.abstractmethod
    async def get_all(self, session: AsyncSession) -> list[TagDTO]: ...
