from fastapi import APIRouter
from starlette import status

from conduit.api.mappers.article_mapper import (
    request_to_create_article_dto,
    request_to_update_article_dto,
)
from conduit.api.schemas.requests.article import (
    CreateArticleRequest,
    UpdateArticleRequest,
)
from conduit.api.schemas.responses.article import ArticleResponse, ArticlesFeedResponse
from conduit.core.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    IArticleService,
    Pagination,
    QueryFilters,
    UnitOfWork,
)

router = APIRouter()


@router.get("/feed", response_model=ArticlesFeedResponse)
async def get_article_feed(
    pagination: Pagination,
    uow: UnitOfWork,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticlesFeedResponse:
    """
    Get article feed from following users.
    """
    articles_feed_dto = await article_service.get_articles_feed(
        uow=uow,
        current_user=current_user,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return ArticlesFeedResponse.from_dto(dto=articles_feed_dto)


@router.get("", response_model=ArticlesFeedResponse)
async def get_global_article_feed(
    pagination: Pagination,
    articles_filters: QueryFilters,
    uow: UnitOfWork,
    current_user: CurrentOptionalUser,
    article_service: IArticleService,
) -> ArticlesFeedResponse:
    """
    Get global article feed.
    """
    articles_feed_dto = await article_service.get_articles_by_filters(
        uow=uow,
        current_user=current_user,
        tag=articles_filters.tag,
        author=articles_filters.author,
        favorited=articles_filters.favorited,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return ArticlesFeedResponse.from_dto(dto=articles_feed_dto)


@router.get("/{slug}", response_model=ArticleResponse)
async def get_article(
    slug: str,
    uow: UnitOfWork,
    current_user: CurrentOptionalUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Get new article by slug.
    """
    article_dto = await article_service.get_article_by_slug(
        uow=uow, slug=slug, current_user=current_user
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.post("", response_model=ArticleResponse)
async def create_article(
    payload: CreateArticleRequest,
    uow: UnitOfWork,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Create new article.
    """
    article_dto = await article_service.create_new_article(
        uow=uow,
        author_id=current_user.id,
        article_to_create=request_to_create_article_dto(payload),
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.put("/{slug}", response_model=ArticleResponse)
async def update_article(
    slug: str,
    payload: UpdateArticleRequest,
    uow: UnitOfWork,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Update an article.
    """
    article_dto = await article_service.update_article_by_slug(
        uow=uow,
        slug=slug,
        article_to_update=request_to_update_article_dto(payload),
        current_user=current_user,
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    slug: str,
    uow: UnitOfWork,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> None:
    """
    Delete an article by slug.
    """
    await article_service.delete_article_by_slug(
        uow=uow, slug=slug, current_user=current_user
    )


@router.post("/{slug}/favorite", response_model=ArticleResponse)
async def favorite_article(
    slug: str,
    uow: UnitOfWork,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Favorite an article.
    """
    article_dto = await article_service.add_article_into_favorites(
        uow=uow, slug=slug, current_user=current_user
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.delete("/{slug}/favorite", response_model=ArticleResponse)
async def unfavorite_article(
    slug: str,
    uow: UnitOfWork,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Unfavorite an article.
    """
    article_dto = await article_service.remove_article_from_favorites(
        uow=uow, slug=slug, current_user=current_user
    )
    return ArticleResponse.from_dto(dto=article_dto)
