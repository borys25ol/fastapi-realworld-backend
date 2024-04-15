import datetime

from pydantic import BaseModel, ConfigDict, Field

from conduit.core.utils.date import convert_datetime_to_realworld
from conduit.domain.dtos.comment import CommentDTO, CommentsListDTO


class CommentAuthorData(BaseModel):
    username: str
    bio: str
    image: str | None
    following: bool


class CommentData(BaseModel):
    id: int
    body: str
    author: CommentAuthorData
    created_at: datetime.datetime = Field(alias="createdAt")
    updated_at: datetime.datetime = Field(alias="updatedAt")

    model_config = ConfigDict(
        json_encoders={datetime.datetime: convert_datetime_to_realworld}
    )


class CommentResponse(BaseModel):
    comment: CommentData

    @classmethod
    def from_dto(cls, dto: CommentDTO) -> "CommentResponse":
        comment = CommentData(
            id=dto.id,
            body=dto.body,
            createdAt=dto.created_at,
            updatedAt=dto.updated_at,
            author=CommentAuthorData(
                username=dto.author.username,
                bio=dto.author.bio,
                image=dto.author.image,
                following=dto.author.following,
            ),
        )
        return CommentResponse(comment=comment)


class CommentsListResponse(BaseModel):
    comments: list[CommentData]
    commentsCount: int

    @classmethod
    def from_dto(cls, dto: CommentsListDTO) -> "CommentsListResponse":
        comments = [
            CommentResponse.from_dto(dto=comment_dto).comment
            for comment_dto in dto.comments
        ]
        return CommentsListResponse(comments=comments, commentsCount=dto.comments_count)
