import datetime

from conduit.application.dtos.article import CreateArticleDTO
from conduit.application.dtos.user import CreateUserDTO, UserDTO
from conduit.application.services.user import IUserService
from conduit.core.utils.slug import make_slug_from_title
from conduit.domain.entities.article import Article
from conduit.domain.uow import IUnitOfWork


async def create_another_test_user(
    uow: IUnitOfWork, user_service: IUserService
) -> UserDTO:
    create_user_dto = CreateUserDTO(
        username="temp-user", email="temp-user@gmail.com", password="password"
    )
    return await user_service.create_user(uow=uow, user_to_create=create_user_dto)


async def create_another_test_article(uow: IUnitOfWork, author_id: int) -> Article:
    create_article_dto = CreateArticleDTO(
        title="One More Test Article",
        description="Test Description",
        body="Test Body Content",
        tags=["tag1", "tag2", "tag3"],
    )
    article = Article(
        id=0,
        author_id=author_id,
        slug=make_slug_from_title(title=create_article_dto.title),
        title=create_article_dto.title,
        description=create_article_dto.description,
        body=create_article_dto.body,
        created_at=datetime.datetime.now(),
        updated_at=None,
    )
    return await uow.articles.add(article)
