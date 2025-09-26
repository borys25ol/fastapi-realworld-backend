from fastapi import APIRouter
from starlette import status

from conduit.api.schemas.requests.article import (
    CreateArticleRequest,
    UpdateArticleRequest,
)
from conduit.api.schemas.responses.article import ArticleResponse, ArticlesFeedResponse
from conduit.core.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    DBSession,
    IArticleService,
    Pagination,
    QueryFilters,
)

router = APIRouter()


@router.get("/feed", response_model=ArticlesFeedResponse)
async def get_article_feed(
    pagination: Pagination,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticlesFeedResponse:
    """
    Get article feed from following users.
    """
    articles_feed_dto = await article_service.get_articles_feed_v2(
        session=session,
        current_user=current_user,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return ArticlesFeedResponse.from_dto(dto=articles_feed_dto)


@router.get("", response_model=ArticlesFeedResponse)
async def get_global_article_feed(
    pagination: Pagination,
    articles_filters: QueryFilters,
    session: DBSession,
    current_user: CurrentOptionalUser,
    article_service: IArticleService,
) -> ArticlesFeedResponse:
    """
    Get global article feed.
    """
    articles_feed_dto = await article_service.get_articles_by_filters_v2(
        session=session,
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
    session: DBSession,
    current_user: CurrentOptionalUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Get new article by slug.
    """
    article_dto = await article_service.get_article_by_slug(
        session=session, slug=slug, current_user=current_user
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.post("", response_model=ArticleResponse)
async def create_article(
    payload: CreateArticleRequest,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Create new article.
    """
    article_dto = await article_service.create_new_article(
        session=session, author_id=current_user.id, article_to_create=payload.to_dto()
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.put("/{slug}", response_model=ArticleResponse)
async def update_article(
    slug: str,
    payload: UpdateArticleRequest,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Update an article.
    """
    article_dto = await article_service.update_article_by_slug(
        session=session,
        slug=slug,
        article_to_update=payload.to_dto(),
        current_user=current_user,
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.delete("/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    slug: str,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> None:
    """
    Delete an article by slug.
    """
    await article_service.delete_article_by_slug(
        session=session, slug=slug, current_user=current_user
    )


@router.post("/{slug}/favorite", response_model=ArticleResponse)
async def favorite_article(
    slug: str,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Favorite an article.
    """
    article_dto = await article_service.add_article_into_favorites(
        session=session, slug=slug, current_user=current_user
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.delete("/{slug}/favorite", response_model=ArticleResponse)
async def unfavorite_article(
    slug: str,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """
    Unfavorite an article.
    """
    article_dto = await article_service.remove_article_from_favorites(
        session=session, slug=slug, current_user=current_user
    )
    return ArticleResponse.from_dto(dto=article_dto)
