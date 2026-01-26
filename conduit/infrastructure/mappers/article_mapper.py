"""Article ORM mappers."""

from conduit.domain.entities.article import Article as ArticleEntity
from conduit.infrastructure.models import Article


def model_to_entity(model: Article) -> ArticleEntity:
    return ArticleEntity(
        id=model.id,
        author_id=model.author_id,
        slug=model.slug,
        title=model.title,
        description=model.description,
        body=model.body,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
