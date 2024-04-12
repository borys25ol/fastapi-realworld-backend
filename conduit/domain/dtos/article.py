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
class ArticleWithMetaDTO:
    id: int
    author_id: int
    slug: str
    title: str
    description: str
    body: str
    tags: list[str]
    author: ProfileDTO
    created_at: str
    updated_at: str
    favorited: bool
    favorites_count: int


@dataclass(frozen=True)
class ArticlesFeedDTO:
    articles: list[ArticleWithMetaDTO]
    articles_count: int


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
