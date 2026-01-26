import datetime
from dataclasses import dataclass


@dataclass(frozen=True)
class ArticleFeedRecordDTO:
    id: int
    author_id: int
    slug: str
    title: str
    description: str
    body: str
    tags: list[str]
    author_username: str
    author_bio: str | None
    author_image_url: str | None
    author_following: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    favorited: bool
    favorites_count: int
