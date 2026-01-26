from conduit.application.dtos.tag import TagDTO
from conduit.application.mappers.tag_mapper import entity_to_tag_dto
from conduit.application.services.tag import ITagService
from conduit.domain.uow import IUnitOfWork


class TagService(ITagService):
    """Service to handle article tags logic."""

    async def get_all_tags(self, uow: IUnitOfWork) -> list[TagDTO]:
        tags = await uow.tags.list()
        return [entity_to_tag_dto(tag) for tag in tags]
