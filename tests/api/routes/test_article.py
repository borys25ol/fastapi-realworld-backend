import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.api.schemas.responses.article import ArticleResponse
from conduit.domain.dtos.article import ArticleDTO
from conduit.infrastructure.repositories.article import ArticleRepository
from conduit.infrastructure.repositories.user import UserRepository
from tests.utils import create_another_test_article, create_another_test_user


@pytest.mark.anyio
async def test_user_can_create_new_article(authorized_test_client: AsyncClient) -> None:
    payload = {
        "article": {
            "title": "Test Article",
            "body": "test body",
            "description": "test description",
            "tagList": ["tag1", "tag2", "tag3"],
        }
    }
    response = await authorized_test_client.post(url="/articles", json=payload)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_user_can_create_article_without_tags(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    payload = {
        "article": {
            "title": "Test Article",
            "body": "test body",
            "description": "test description",
            "tagList": [],
        }
    }
    response = await authorized_test_client.post(url="/articles", json=payload)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_user_can_create_article_without_duplicated_tags(
    authorized_test_client: AsyncClient,
) -> None:
    payload = {
        "article": {
            "title": "Test Article",
            "body": "test body",
            "description": "test description",
            "tagList": ["tag1", "tag2", "tag2", "tag3", "tag3"],
        }
    }
    response = await authorized_test_client.post(url="/articles", json=payload)
    article = ArticleResponse(**response.json())
    assert set(article.article.tags) == {"tag1", "tag2", "tag3"}


@pytest.mark.anyio
async def test_user_can_create_article_with_existing_title(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    payload = {
        "article": {
            "title": test_article.title,
            "body": "test body",
            "description": "test description",
            "tagList": test_article.tags,
        }
    }
    response = await authorized_test_client.post(url="/articles", json=payload)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_user_can_not_retrieve_not_existing_article(
    authorized_test_client: AsyncClient,
) -> None:
    response = await authorized_test_client.get(
        url="/articles/not-existing-article-slug"
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_user_can_retrieve_article_if_exists(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.get(url=f"/articles/{test_article.slug}")
    article = ArticleResponse(**response.json())
    assert article.article.slug == test_article.slug
    assert article.article.description == test_article.description
    assert article.article.body == test_article.body


@pytest.mark.anyio
async def test_user_can_not_delete_foreign_article(
    authorized_test_client: AsyncClient,
    session: AsyncSession,
    user_repository: UserRepository,
    article_repository: ArticleRepository,
) -> None:
    new_user = await create_another_test_user(
        session=session, user_repository=user_repository
    )
    new_article = await create_another_test_article(
        session=session, article_repository=article_repository, author_id=new_user.id
    )
    response = await authorized_test_client.delete(url=f"/articles/{new_article.slug}")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_can_not_update_foreign_article(
    authorized_test_client: AsyncClient,
    session: AsyncSession,
    user_repository: UserRepository,
    article_repository: ArticleRepository,
) -> None:
    new_user = await create_another_test_user(
        session=session, user_repository=user_repository
    )
    new_article = await create_another_test_article(
        session=session, article_repository=article_repository, author_id=new_user.id
    )
    response = await authorized_test_client.put(
        url=f"/articles/{new_article.slug}",
        json={"article": {"title": "New Updated Title"}},
    )
    assert response.status_code == 403


@pytest.mark.anyio
async def test_user_can_delete_own_article(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.delete(url=f"/articles/{test_article.slug}")
    assert response.status_code == 204

    response = await authorized_test_client.get(url=f"/articles/{test_article.slug}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_user_can_create_draft(
    authorized_test_client: AsyncClient,
) -> None:
    payload = {
        "article": {
            "title": "Draft Article",
            "body": "draft body",
            "description": "draft description",
            "tagList": ["draft"],
        }
    }
    response = await authorized_test_client.post("/articles/draft", json=payload)
    assert response.status_code == 200
    data = response.json()["article"]
    assert data["title"] == "Draft Article"


@pytest.mark.anyio
async def test_only_author_can_see_draft(
    authorized_test_client: AsyncClient,
    another_authorized_client: AsyncClient,
    test_article: ArticleDTO,
) -> None:
    # Create draft with first user
    payload = {
        "article": {
            "title": "Draft Article",
            "body": "draft body",
            "description": "draft description",
            "tagList": ["draft"],
        }
    }
    response = await authorized_test_client.post("/articles/draft", json=payload)
    slug = response.json()["article"]["slug"]
    
    # Try to access with another user
    response = await another_authorized_client.get(f"/articles/{slug}")
    assert response.status_code == 403


@pytest.mark.anyio
async def test_draft_excluded_from_feed(
    authorized_test_client: AsyncClient,
) -> None:
    # Create draft
    payload = {
        "article": {
            "title": "Draft Article",
            "body": "draft body",
            "description": "draft description",
            "tagList": ["draft"],
        }
    }
    await authorized_test_client.post("/articles/draft", json=payload)
    
    # Check global feed
    response = await authorized_test_client.get("/articles")
    articles = response.json()["articles"]
    titles = [article["title"] for article in articles]
    assert "Draft Article" not in titles
