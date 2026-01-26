from conduit.core.exceptions import CommentCreateException
from conduit.domain.dtos.comment import CommentDTO, CommentsListDTO, CreateCommentDTO
from conduit.domain.dtos.profile import ProfileDTO
from conduit.domain.dtos.user import UserDTO
from conduit.domain.entities.comment import Comment
from conduit.domain.services.comment import ICommentService
from conduit.domain.services.profile import IProfileService
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
            comment = await uow.comments.add(
                author_id=current_user.id,
                article_id=article.id,
                create_item=comment_to_create,
            )
        except Exception as exc:
            raise CommentCreateException() from exc
        return CommentDTO(
            id=comment.id,
            body=comment.body,
            author=profile,
            created_at=comment.created_at,
            updated_at=comment.updated_at or comment.created_at,
        )

    async def get_article_comments(
        self, uow: IUnitOfWork, slug: str, current_user: UserDTO | None = None
    ) -> CommentsListDTO:
        article = await uow.articles.get_by_slug(slug=slug)
        comments = await uow.comments.list(article_id=article.id)
        profiles_map = await self._get_profiles_mapping(
            uow=uow, comments=comments, current_user=current_user
        )
        comments = [
            CommentDTO(
                id=comment_entity.id,
                body=comment_entity.body,
                author=profiles_map[comment_entity.author_id],
                created_at=comment_entity.created_at,
                updated_at=comment_entity.updated_at or comment_entity.created_at,
            )
            for comment_entity in comments
        ]
        comments_count = await uow.comments.count(article_id=article.id)
        return CommentsListDTO(comments=comments, comments_count=comments_count)

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
