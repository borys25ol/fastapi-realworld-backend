from pydantic import BaseModel, Field


class CreateCommentData(BaseModel):
    body: str = Field(..., min_length=1)


class CreateCommentRequest(BaseModel):
    comment: CreateCommentData
