import abc

from conduit.domain.dtos.tag import TagDTO
from conduit.domain.uow import IUnitOfWork


class ITagService(abc.ABC):
    @abc.abstractmethod
    async def get_all_tags(self, uow: IUnitOfWork) -> list[TagDTO]: ...
