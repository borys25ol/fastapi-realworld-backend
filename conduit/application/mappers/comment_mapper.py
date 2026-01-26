from conduit.application.dtos.comment import CommentDTO, CommentsListDTO
from conduit.application.dtos.profile import ProfileDTO
from conduit.domain.entities.comment import Comment


def entity_to_comment_dto(comment: Comment, author: ProfileDTO) -> CommentDTO:
    return CommentDTO(
        id=comment.id,
        body=comment.body,
        author=author,
        created_at=comment.created_at,
        updated_at=comment.updated_at or comment.created_at,
    )


def comments_to_list_dto(
    comments: list[CommentDTO], comments_count: int
) -> CommentsListDTO:
    return CommentsListDTO(comments=comments, comments_count=comments_count)
