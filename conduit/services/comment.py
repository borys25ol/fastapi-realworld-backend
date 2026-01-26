from datetime import datetime

from conduit.application.dtos.comment import (
    CommentDTO,
    CommentsListDTO,
    CreateCommentDTO,
)
from conduit.application.dtos.profile import ProfileDTO
from conduit.application.dtos.user import UserDTO
from conduit.application.mappers.comment_mapper import (
    comments_to_list_dto,
    entity_to_comment_dto,
)
from conduit.application.services.comment import ICommentService
from conduit.application.services.profile import IProfileService
from conduit.core.exceptions import CommentCreateException
from conduit.domain.entities.comment import Comment
from conduit.domain.uow import IUnitOfWork


class CommentService(ICommentService):
    def __init__(self, profile_service: IProfileService) -> None:
        self._profile_service = profile_service

    async def create_article_comment(
        self,
        uow: IUnitOfWork,
        slug: str,
        comment_to_create: CreateCommentDTO,
        current_user: UserDTO,
    ) -> CommentDTO:
        article = await uow.articles.get_by_slug(slug=slug)
        profile = ProfileDTO(
            user_id=current_user.id,
            username=current_user.username,
            bio=current_user.bio,
            image=current_user.image_url,
            following=False,
        )
        try:
            new_comment = Comment(
                id=0,
                body=comment_to_create.body,
                author_id=current_user.id,
                article_id=article.id,
                created_at=datetime.now(),
                updated_at=None,
            )
            comment = await uow.comments.add(new_comment)
        except Exception as exc:
            raise CommentCreateException() from exc
        return entity_to_comment_dto(comment=comment, author=profile)

    async def get_article_comments(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO | None = None
    ) -> CommentsListDTO:
        article = await uow.articles.get_by_slug(slug=slug)
        comments = await uow.comments.list(article_id=article.id)
        profiles_map = await self._get_profiles_mapping(
            uow=uow, comments=comments, current_user=current_user
        )
        comments = [
            entity_to_comment_dto(
                comment=comment_entity, author=profiles_map[comment_entity.author_id]
            )
            for comment_entity in comments
        ]
        comments_count = await uow.comments.count(article_id=article.id)
        return comments_to_list_dto(comments=comments, comments_count=comments_count)

    async def delete_article_comment(
        self, uow: IUnitOfWork, slug: str, comment_id: int, current_user: UserDTO
    ) -> None:
        # Check if article exists before deleting the comment.
        await uow.articles.get_by_slug(slug=slug)

        comment = await uow.comments.get(comment_id=comment_id)
        comment.assert_owner(user_id=current_user.id)

        await uow.comments.delete(comment_id=comment_id)

    async def _get_profiles_mapping(
        self, uow: IUnitOfWork, comments: list[Comment], current_user: UserDTO | None
    ) -> dict[int, ProfileDTO]:
        comments_profiles = await self._profile_service.get_profiles_by_user_ids(
            uow=uow,
            user_ids=list({comment.author_id for comment in comments}),
            current_user=current_user,
        )
        return {profile.user_id: profile for profile in comments_profiles}
