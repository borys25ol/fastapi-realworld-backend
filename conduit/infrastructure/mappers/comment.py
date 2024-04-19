from conduit.domain.dtos.comment import CommentRecordDTO
from conduit.domain.mapper import IModelMapper
from conduit.infrastructure.models import Comment


class CommentModelMapper(IModelMapper[Comment, CommentRecordDTO]):

    @staticmethod
    def to_dto(model: Comment) -> CommentRecordDTO:
        dto = CommentRecordDTO(
            id=model.id,
            body=model.body,
            author_id=model.author_id,
            article_id=model.article_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        return dto

    @staticmethod
    def from_dto(dto: CommentRecordDTO) -> Comment:
        model = Comment(
            body=dto.body,
            author_id=dto.author_id,
            article_id=dto.article_id,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
        if hasattr(dto, "id"):
            model.id = dto.id
        return model
