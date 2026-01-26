from conduit.application.dtos.tag import TagDTO
from conduit.domain.entities.tag import Tag


def entity_to_tag_dto(tag: Tag) -> TagDTO:
    return TagDTO(id=tag.id, tag=tag.tag, created_at=tag.created_at)
