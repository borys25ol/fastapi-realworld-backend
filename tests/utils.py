from sqlalchemy.ext.asyncio import AsyncSession

from conduit.domain.dtos.article import ArticleRecordDTO, CreateArticleDTO
from conduit.domain.dtos.user import CreateUserDTO, UserDTO
from conduit.infrastructure.repositories.article import ArticleRepository
from conduit.infrastructure.repositories.user import UserRepository


async def create_another_test_user(
    session: AsyncSession, user_repository: UserRepository
) -> UserDTO:
    create_user_dto = CreateUserDTO(
        username="temp-user", email="temp-user@gmail.com", password="password"
    )
    return await user_repository.create(session=session, create_item=create_user_dto)


async def create_another_test_article(
    session: AsyncSession, article_repository: ArticleRepository, author_id: int
) -> ArticleRecordDTO:
    create_article_dto = CreateArticleDTO(
        title="One More Test Article",
        description="Test Description",
        body="Test Body",
        tags=["tag1", "tag2", "tag3"],
    )
    return await article_repository.create(
        session=session, author_id=author_id, create_item=create_article_dto
    )
