from fastapi import APIRouter, Path
from starlette import status

from conduit.api.schemas.requests.comment import CreateCommentRequest
from conduit.api.schemas.responses.comment import CommentResponse, CommentsListResponse
from conduit.core.dependencies import (
    CurrentOptionalUser,
    CurrentUser,
    DBSession,
    ICommentService,
)

router = APIRouter()


@router.get("/{slug}/comments", response_model=CommentsListResponse)
async def get_comments(
    slug: str,
    session: DBSession,
    current_user: CurrentOptionalUser,
    comment_service: ICommentService,
) -> CommentsListResponse:
    """
    Get comments for an article.
    """
    comment_list_dto = await comment_service.get_article_comments(
        session=session, slug=slug, current_user=current_user
    )
    return CommentsListResponse.from_dto(dto=comment_list_dto)


@router.post("/{slug}/comments", response_model=CommentResponse)
async def create_comment(
    slug: str,
    payload: CreateCommentRequest,
    session: DBSession,
    current_user: CurrentUser,
    comment_service: ICommentService,
) -> CommentResponse:
    """
    Create a comment for an article.
    """
    comment_dto = await comment_service.create_article_comment(
        session=session,
        slug=slug,
        comment_to_create=payload.to_dto(),
        current_user=current_user,
    )
    return CommentResponse.from_dto(dto=comment_dto)


@router.delete("/{slug}/comments/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    slug: str,
    session: DBSession,
    current_user: CurrentUser,
    comment_service: ICommentService,
    comment_id: int = Path(..., alias="id"),
) -> None:
    """
    Delete a comment for an article.
    """
    await comment_service.delete_article_comment(
        session=session, slug=slug, comment_id=comment_id, current_user=current_user
    )
