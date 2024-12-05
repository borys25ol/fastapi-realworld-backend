from fastapi import APIRouter
from fastapi.params import Query
from starlette import status

from conduit.api.schemas.requests.article import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    CreateArticleRequest,
    UpdateArticleRequest,
)
from conduit.api.schemas.responses.article import ArticleResponse, ArticlesFeedResponse, ArticleVersionsResponse
from conduit.core.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    DBSession,
    IArticleService,
    QueryFilters,
)

router = APIRouter()


@router.get("/feed", response_model=ArticlesFeedResponse)
async def get_article_feed(
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> ArticlesFeedResponse:
    """
    Get article feed from following users.
    """
    articles_feed_dto = await article_service.get_articles_feed_v2(
        session=session, current_user=current_user, limit=limit, offset=offset
    )
    return ArticlesFeedResponse.from_dto(dto=articles_feed_dto)


@router.get("", response_model=ArticlesFeedResponse)
async def get_global_article_feed(
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
        limit=articles_filters.limit,
        offset=articles_filters.offset,
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


@router.post("/draft", response_model=ArticleResponse)
async def create_draft(
    payload: CreateArticleRequest,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """Create new draft article."""
    article_dto = await article_service.create_draft(
        session=session,
        author_id=current_user.id,
        draft_to_create=payload.to_dto(),
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.get("/drafts", response_model=ArticlesFeedResponse)
async def list_drafts(
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
    limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
    offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> ArticlesFeedResponse:
    """List user's draft articles."""
    feed_dto = await article_service.list_user_drafts(
        session=session,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )
    return ArticlesFeedResponse.from_dto(dto=feed_dto)


@router.put("/{slug}/publish", response_model=ArticleResponse)
async def publish_draft(
    slug: str,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleResponse:
    """Publish a draft article."""
    article_dto = await article_service.publish_draft(
        session=session,
        slug=slug,
        current_user=current_user,
    )
    return ArticleResponse.from_dto(dto=article_dto)


@router.get("/{slug}/versions", response_model=ArticleVersionsResponse)
async def get_article_versions(
    slug: str,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
) -> ArticleVersionsResponse:
    """Get article version history."""
    versions = await article_service.get_article_versions(
        session=session,
        slug=slug,
        current_user=current_user,
    )
    return ArticleVersionsResponse(versions=versions)
