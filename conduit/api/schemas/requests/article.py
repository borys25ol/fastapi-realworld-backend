from pydantic import BaseModel, Field

from conduit.domain.dtos.article import CreateArticleDTO, UpdateArticleDTO

DEFAULT_ARTICLES_LIMIT = 20
DEFAULT_ARTICLES_OFFSET = 0


class ArticlesFilters(BaseModel):
    tag: str | None = None
    author: str | None = None
    favorited: str | None = None
    limit: int = Field(DEFAULT_ARTICLES_LIMIT, ge=1)
    offset: int = Field(DEFAULT_ARTICLES_OFFSET, ge=0)


class CreateArticleData(BaseModel):
    title: str
    description: str
    body: str
    tags: list[str] = Field(alias="tagList")


class UpdateArticleData(BaseModel):
    title: str
    description: str
    body: str


class UpdateArticleRequest(BaseModel):
    article: UpdateArticleData

    def to_dto(self) -> UpdateArticleDTO:
        return UpdateArticleDTO(
            title=self.article.title,
            description=self.article.description,
            body=self.article.body,
        )


class CreateArticleRequest(BaseModel):
    article: CreateArticleData

    def to_dto(self) -> CreateArticleDTO:
        return CreateArticleDTO(
            title=self.article.title,
            description=self.article.description,
            body=self.article.body,
            tags=self.article.tags,
        )
