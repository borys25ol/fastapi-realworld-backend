import datetime
from dataclasses import dataclass

from conduit.domain.dtos.profile import ProfileDTO


@dataclass(frozen=True)
class CommentRecordDTO:
    id: int
    body: str
    author_id: int
    article_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class CommentDTO:
    id: int
    body: str
    author: ProfileDTO
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class CommentsListDTO:
    comments: list[CommentDTO]
    comments_count: int


@dataclass(frozen=True)
class CreateCommentDTO:
    body: str
