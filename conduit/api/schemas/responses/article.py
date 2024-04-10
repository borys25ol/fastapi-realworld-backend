import datetime

from pydantic import BaseModel, Field

from conduit.domain.dtos.article import ArticlesFeedDTO, ArticleWithExtraDTO
from conduit.domain.dtos.profile import ProfileDTO


class ArticleAuthorData(BaseModel):
    username: str
    bio: str
    image: str | None
    following: bool


class ArticleData(BaseModel):
    slug: str
    title: str
    description: str
    body: str
    tags: list[str] = Field(alias="tagList")
    created_at: datetime.datetime = Field(alias="createdAt")
    updated_at: datetime.datetime = Field(alias="updatedAt")
    favorited: bool = False
    favorites_count: int = Field(default=0, alias="favoritesCount")
    author: ArticleAuthorData


class ArticleResponse(BaseModel):
    article: ArticleData

    @classmethod
    def from_dto(
        cls, article_dto: ArticleWithExtraDTO, profile_dto: ProfileDTO
    ) -> "ArticleResponse":
        article = ArticleData(
            slug=article_dto.article.slug,
            title=article_dto.article.title,
            description=article_dto.article.description,
            body=article_dto.article.body,
            tagList=article_dto.tags,
            createdAt=article_dto.article.created_at,
            updatedAt=article_dto.article.updated_at,
            favorited=article_dto.favorited,
            favorites_count=article_dto.favorites_count,
            author=ArticleAuthorData(
                username=profile_dto.username,
                bio=profile_dto.bio,
                image=profile_dto.image,
                following=profile_dto.following,
            ),
        )
        return ArticleResponse(article=article)


class ArticlesFeedResponse(BaseModel):
    articles: list[ArticleData]
    articles_count: int = Field(alias="articlesCount")

    @classmethod
    def from_dto(
        cls, articles_feed_dto: ArticlesFeedDTO, profiles_dto_map: dict[int, ProfileDTO]
    ) -> "ArticlesFeedResponse":
        articles = [
            ArticleResponse.from_dto(
                article_dto=article,
                profile_dto=profiles_dto_map[article.article.author_id],
            ).article
            for article in articles_feed_dto.articles
        ]
        return ArticlesFeedResponse(
            articles=articles, articlesCount=articles_feed_dto.articles_count
        )
