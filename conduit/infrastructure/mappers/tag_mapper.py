"""Tag ORM mappers."""

from conduit.domain.entities.tag import Tag as TagEntity
from conduit.infrastructure.models import Tag


def model_to_entity(model: Tag) -> TagEntity:
    return TagEntity(id=model.id, tag=model.tag, created_at=model.created_at)
