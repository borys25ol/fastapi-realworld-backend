from pydantic import BaseModel

from conduit.domain.dtos.comment import CreateCommentDTO


class CreateCommentData(BaseModel):
    body: str


class CreateCommentRequest(BaseModel):
    comment: CreateCommentData

    def to_dto(self) -> CreateCommentDTO:
        return CreateCommentDTO(body=self.comment.body)
