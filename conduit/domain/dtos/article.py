import datetime
from dataclasses import dataclass

from conduit.domain.dtos.profile import ProfileDTO


@dataclass(frozen=True)
class ArticleDTO:
    id: int
    author_id: int
    slug: str
    title: str
    description: str
    body: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ArticleWithExtraDTO:
    article: ArticleDTO
    profile: ProfileDTO
    tags: list[str]
    favorited: bool
    favorites_count: int


@dataclass(frozen=True)
class ArticlesFeedDTO:
    articles: list[ArticleWithExtraDTO]
    articles_count: int


@dataclass(frozen=True)
class ArticleAuthorDTO:
    username: str
    bio: str
    image: str | None
    following: bool


@dataclass(frozen=True)
class ArticleResponseDTO:
    slug: str
    title: str
    description: str
    body: str
    tags: list[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    favorited: bool
    favorites_count: int
    author: ArticleAuthorDTO


@dataclass(frozen=True)
class CreateArticleDTO:
    title: str
    description: str
    body: str
    tags: list[str]


@dataclass(frozen=True)
class UpdateArticleDTO:
    title: str
    description: str
    body: str
