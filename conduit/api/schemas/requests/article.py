from pydantic import BaseModel, Field


class ArticlesPagination(BaseModel):
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)


class ArticlesFilters(BaseModel):
    tag: str | None = None
    author: str | None = None
    favorited: str | None = None


class CreateArticleData(BaseModel):
    title: str = Field(..., min_length=5)
    description: str = Field(min_length=10)
    body: str = Field(min_length=10)
    tags: list[str] = Field(alias="tagList")


class UpdateArticleData(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    body: str | None = Field(None)


class UpdateArticleRequest(BaseModel):
    article: UpdateArticleData


class CreateArticleRequest(BaseModel):
    article: CreateArticleData
