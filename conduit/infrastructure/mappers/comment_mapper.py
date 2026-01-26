"""Comment ORM mappers."""

from conduit.domain.entities.comment import Comment as CommentEntity
from conduit.infrastructure.models import Comment


def model_to_entity(model: Comment) -> CommentEntity:
    return CommentEntity(
        id=model.id,
        body=model.body,
        author_id=model.author_id,
        article_id=model.article_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
