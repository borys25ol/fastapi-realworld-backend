from pydantic import BaseModel, Field

from conduit.domain.dtos.comment import CreateCommentDTO


class CreateCommentData(BaseModel):
    body: str = Field(..., min_length=1)


class CreateCommentRequest(BaseModel):
    comment: CreateCommentData

    def to_dto(self) -> CreateCommentDTO:
        return CreateCommentDTO(body=self.comment.body)
