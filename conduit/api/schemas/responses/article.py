import datetime

from pydantic import BaseModel, ConfigDict, Field

from conduit.core.utils.date import convert_datetime_to_realworld
from conduit.domain.dtos.article import ArticleDTO, ArticlesFeedDTO


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

    model_config = ConfigDict(
        json_encoders={datetime.datetime: convert_datetime_to_realworld}
    )


class ArticleResponse(BaseModel):
    article: ArticleData

    @classmethod
    def from_dto(cls, dto: ArticleDTO) -> "ArticleResponse":
        article = ArticleData(
            slug=dto.slug,
            title=dto.title,
            description=dto.description,
            body=dto.body,
            tagList=dto.tags,
            createdAt=dto.created_at,
            updatedAt=dto.updated_at,
            favorited=dto.favorited,
            favoritesCount=dto.favorites_count,
            author=ArticleAuthorData(
                username=dto.author.username,
                bio=dto.author.bio,
                image=dto.author.image,
                following=dto.author.following,
            ),
        )
        return ArticleResponse(article=article)


class ArticlesFeedResponse(BaseModel):
    articles: list[ArticleData]
    articles_count: int = Field(alias="articlesCount")

    @classmethod
    def from_dto(cls, dto: ArticlesFeedDTO) -> "ArticlesFeedResponse":
        articles = [
            ArticleResponse.from_dto(dto=article_dto).article
            for article_dto in dto.articles
        ]
        return ArticlesFeedResponse(articles=articles, articlesCount=dto.articles_count)
