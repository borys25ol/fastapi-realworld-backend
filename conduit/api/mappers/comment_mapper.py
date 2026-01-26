from conduit.api.schemas.requests.comment import CreateCommentRequest
from conduit.application.dtos.comment import CreateCommentDTO


def request_to_create_comment_dto(request: CreateCommentRequest) -> CreateCommentDTO:
    return CreateCommentDTO(body=request.comment.body)
