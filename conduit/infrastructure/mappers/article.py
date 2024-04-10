from conduit.domain.dtos.article import ArticleDTO
from conduit.domain.mapper import IModelMapper
from conduit.infrastructure.models import Article


class ArticleModelMapper(IModelMapper[Article, ArticleDTO]):

    @staticmethod
    def to_dto(model: Article) -> ArticleDTO:
        dto = ArticleDTO(
            id=model.id,
            author_id=model.author_id,
            slug=model.slug,
            title=model.title,
            description=model.description,
            body=model.body,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        return dto

    @staticmethod
    def from_dto(dto: ArticleDTO) -> Article:
        model = Article(
            author_id=dto.author_id,
            slug=dto.slug,
            title=dto.title,
            description=dto.description,
            body=dto.body,
            created_at=dto.created_at,
        )
        if hasattr(dto, "id"):
            model.id = dto.id
        return model
