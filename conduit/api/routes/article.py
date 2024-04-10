from fastapi import APIRouter

from conduit.api.schemas.requests.article import CreateArticleRequest
from conduit.api.schemas.responses.article import ArticleResponse, ArticlesFeedResponse
from conduit.core.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    DBSession,
    IArticleService,
)

router = APIRouter()


@router.get("/feed", response_model=ArticlesFeedResponse)
async def get_article_feed(
    session: DBSession, current_user: CurrentUser, article_service: IArticleService
) -> ArticlesFeedResponse:
    """
    Get article feed from following users.
    """
    articles_feed_dto = await article_service.get_articles_by_following_authors(
        session=session, current_user=current_user
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
