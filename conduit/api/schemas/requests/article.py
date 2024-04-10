from pydantic import BaseModel, Field

from conduit.domain.dtos.article import CreateArticleDTO


class CreateArticleData(BaseModel):
    title: str
    description: str
    body: str
    tags: list[str] = Field(alias="tagList")


class CreateArticleRequest(BaseModel):
    article: CreateArticleData

    def to_dto(self) -> CreateArticleDTO:
        return CreateArticleDTO(
            title=self.article.title,
            description=self.article.description,
            body=self.article.body,
            tags=self.article.tags,
        )
