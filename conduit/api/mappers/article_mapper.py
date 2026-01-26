from conduit.api.schemas.requests.article import (
    CreateArticleRequest,
    UpdateArticleRequest,
)
from conduit.application.dtos.article import CreateArticleDTO, UpdateArticleDTO


def request_to_create_article_dto(request: CreateArticleRequest) -> CreateArticleDTO:
    return CreateArticleDTO(
        title=request.article.title,
        description=request.article.description,
        body=request.article.body,
        tags=request.article.tags,
    )


def request_to_update_article_dto(request: UpdateArticleRequest) -> UpdateArticleDTO:
    return UpdateArticleDTO(
        title=request.article.title,
        description=request.article.description,
        body=request.article.body,
    )
