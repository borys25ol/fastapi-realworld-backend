import datetime

from pydantic import BaseModel, Field

from conduit.domain.dtos.article import ArticlesFeedDTO, ArticleWithExtraDTO


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
    def from_dto(cls, dto: ArticleWithExtraDTO) -> "ArticleResponse":
        article = ArticleData(
            slug=dto.article.slug,
            title=dto.article.title,
            description=dto.article.description,
            body=dto.article.body,
            tagList=dto.tags,
            createdAt=dto.article.created_at,
            updatedAt=dto.article.updated_at,
            favorited=dto.favorited,
            favoritesCount=dto.favorites_count,
            author=ArticleAuthorData(
                username=dto.profile.username,
                bio=dto.profile.bio,
                image=dto.profile.image,
                following=dto.profile.following,
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
