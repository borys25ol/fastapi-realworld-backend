from conduit.domain.dtos.tag import TagDTO, TagRecordDTO
from conduit.domain.services.tag import ITagService
from conduit.domain.uow import IUnitOfWork


class TagService(ITagService):
    """Service to handle article tags logic."""

    async def get_all_tags(self, uow: IUnitOfWork) -> list[TagDTO]:
        tags = await uow.tags.list()
        return [self._to_tag_dto(tag) for tag in tags]

    @staticmethod
    def _to_tag_dto(record: TagRecordDTO) -> TagDTO:
        return TagDTO(id=record.id, tag=record.tag, created_at=record.created_at)
