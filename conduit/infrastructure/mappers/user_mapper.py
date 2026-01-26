"""User ORM mappers."""

from conduit.domain.entities.user import User as UserEntity
from conduit.infrastructure.models import User


def model_to_entity(model: User) -> UserEntity:
    return UserEntity(
        id=model.id,
        username=model.username,
        email=model.email,
        password_hash=model.password_hash,
        bio=model.bio,
        image_url=model.image_url or "",
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
