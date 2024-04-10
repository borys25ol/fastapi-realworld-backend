from fastapi import APIRouter

from conduit.api.schemas.requests.article import CreateArticleRequest
from conduit.api.schemas.responses.article import ArticleResponse, ArticlesFeedResponse
from conduit.core.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    DBSession,
    IArticleService,
    IProfileService,
)

router = APIRouter()


@router.get("/feed", response_model=ArticlesFeedResponse)
async def get_article_feed(
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
    profile_service: IProfileService,
) -> ArticlesFeedResponse:
    """
    Get article feed from following users.
    """
    followed_profiles_map = await profile_service.get_followed_profiles(
        session=session, current_user=current_user
    )
    articles_feed_dto = await article_service.get_articles_by_following_authors(
        session=session, following_author_ids=list(followed_profiles_map.keys())
    )
    return ArticlesFeedResponse.from_dto(
        articles_feed_dto=articles_feed_dto, profiles_dto_map=followed_profiles_map
    )


@router.get("/{slug}", response_model=ArticleResponse)
async def get_article(
    slug: str,
    session: DBSession,
    current_user: CurrentOptionalUser,
    article_service: IArticleService,
    profile_service: IProfileService,
) -> ArticleResponse:
    """
    Get new article by slug.
    """
    user_id = current_user.id if current_user else None
    article_dto = await article_service.get_article_by_slug(
        session=session, user_id=user_id, slug=slug
    )
    profile_dto = await profile_service.get_profile_by_user_id(
        session=session,
        user_id=article_dto.article.author_id,
        current_user=current_user,
    )
    return ArticleResponse.from_dto(article_dto=article_dto, profile_dto=profile_dto)


@router.post("", response_model=ArticleResponse)
async def create_article(
    payload: CreateArticleRequest,
    session: DBSession,
    current_user: CurrentUser,
    article_service: IArticleService,
    profile_service: IProfileService,
) -> ArticleResponse:
    """
    Create new article.
    """
    created_article_dto = await article_service.create_new_article(
        session=session, author_id=current_user.id, article_to_create=payload.to_dto()
    )
    profile_dto = await profile_service.get_profile_by_username(
        session=session, username=current_user.username, current_user=current_user
    )
    return ArticleResponse.from_dto(
        article_dto=created_article_dto, profile_dto=profile_dto
    )
