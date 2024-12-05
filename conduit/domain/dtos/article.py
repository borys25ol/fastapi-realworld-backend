import datetime
from dataclasses import dataclass, replace

from conduit.domain.dtos.profile import ProfileDTO


@dataclass(frozen=True)
class ArticleRecordDTO:
    id: int
    author_id: int
    slug: str
    title: str
    description: str
    body: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass(frozen=True)
class ArticleAuthorDTO:
    username: str
    bio: str = ""
    image: str | None = None
    following: bool = False
    id: int | None = None


@dataclass(frozen=True)
class ArticleDTO:
    id: int
    author_id: int
    slug: str
    title: str
    description: str
    body: str
    tags: list[str]
    author: ArticleAuthorDTO
    created_at: datetime.datetime
    updated_at: datetime.datetime
    favorited: bool
    favorites_count: int

    @classmethod
    def with_updated_fields(
        cls, dto: "ArticleDTO", updated_fields: dict
    ) -> "ArticleDTO":
        return replace(dto, **updated_fields)


@dataclass(frozen=True)
class ArticlesFeedDTO:
    articles: list[ArticleDTO]
    articles_count: int


@dataclass(frozen=True)
class CreateArticleDTO:
    title: str
    description: str
    body: str
    tags: list[str]


@dataclass(frozen=True)
class UpdateArticleDTO:
    title: str | None
    description: str | None
    body: str | None


@dataclass
class ArticleVersionDTO:
    id: int
    article_id: int
    version: int
    title: str
    description: str
    body: str
    created_at: datetime


@dataclass
class CreateDraftDTO:
    title: str
    description: str
    body: str
    tags: list[str]
