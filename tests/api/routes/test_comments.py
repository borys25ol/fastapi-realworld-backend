import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from conduit.api.schemas.responses.comment import CommentResponse, CommentsListResponse
from conduit.dtos.domain.article import ArticleDTO
from conduit.interfaces.services.user import IUserService
from conduit.core.dependencies import IAuthTokenService
from tests.utils import create_another_test_user


@pytest.mark.anyio
async def test_user_can_add_comment_to_article(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    payload = {"comment": {"body": "This is a great article!"}}
    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/comments", json=payload
    )
    assert response.status_code == 200
    data = CommentResponse(**response.json())
    assert data.comment.body == "This is a great article!"


@pytest.mark.anyio
async def test_comment_response_contains_expected_fields(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    payload = {"comment": {"body": "Checking response shape"}}
    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/comments", json=payload
    )
    assert response.status_code == 200
    comment = response.json()["comment"]
    assert "id" in comment
    assert "body" in comment
    assert "createdAt" in comment
    assert "updatedAt" in comment
    assert "author" in comment
    assert "username" in comment["author"]
    assert "following" in comment["author"]


@pytest.mark.anyio
async def test_user_can_list_comments_for_article(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    for i in range(3):
        await authorized_test_client.post(
            url=f"/articles/{test_article.slug}/comments",
            json={"comment": {"body": f"Comment {i}"}},
        )

    response = await authorized_test_client.get(
        url=f"/articles/{test_article.slug}/comments"
    )
    assert response.status_code == 200
    data = CommentsListResponse(**response.json())
    assert data.commentsCount == 3
    assert len(data.comments) == 3


@pytest.mark.anyio
async def test_unauthenticated_user_can_read_comments(
    test_client: AsyncClient,
    authorized_test_client: AsyncClient,
    test_article: ArticleDTO,
) -> None:
    await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/comments",
        json={"comment": {"body": "Public comment"}},
    )

    response = await test_client.get(url=f"/articles/{test_article.slug}/comments")
    assert response.status_code == 200
    data = CommentsListResponse(**response.json())
    assert data.commentsCount == 1


@pytest.mark.anyio
async def test_user_can_delete_own_comment(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/comments",
        json={"comment": {"body": "To be deleted"}},
    )
    assert response.status_code == 200
    comment_id = response.json()["comment"]["id"]

    response = await authorized_test_client.delete(
        url=f"/articles/{test_article.slug}/comments/{comment_id}"
    )
    assert response.status_code == 204


@pytest.mark.anyio
async def test_deleted_comment_no_longer_appears_in_list(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/comments",
        json={"comment": {"body": "Will be removed"}},
    )
    comment_id = response.json()["comment"]["id"]

    await authorized_test_client.delete(
        url=f"/articles/{test_article.slug}/comments/{comment_id}"
    )

    response = await authorized_test_client.get(
        url=f"/articles/{test_article.slug}/comments"
    )
    data = CommentsListResponse(**response.json())
    assert data.commentsCount == 0
    assert all(c.id != comment_id for c in data.comments)


@pytest.mark.anyio
async def test_user_cannot_delete_another_users_comment(
    application: FastAPI,
    authorized_test_client: AsyncClient,
    test_article: ArticleDTO,
    session: AsyncSession,
    user_service: IUserService,
    auth_token_service: IAuthTokenService,
) -> None:
    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/comments",
        json={"comment": {"body": "Author's own comment"}},
    )
    assert response.status_code == 200
    comment_id = response.json()["comment"]["id"]

    other_user = await create_another_test_user(
        session=session, user_service=user_service
    )
    other_token = auth_token_service.generate_jwt_token(user=other_user)

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers={
            "Authorization": f"Token {other_token}",
            "Content-Type": "application/json",
        },
    ) as other_client:
        response = await other_client.delete(
            url=f"/articles/{test_article.slug}/comments/{comment_id}"
        )

    assert response.status_code == 403


@pytest.mark.anyio
async def test_create_comment_on_nonexistent_article_returns_404(
    authorized_test_client: AsyncClient,
) -> None:
    response = await authorized_test_client.post(
        url="/articles/no-such-article/comments",
        json={"comment": {"body": "Commenting into the void"}},
    )
    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_comments_on_nonexistent_article_returns_404(
    test_client: AsyncClient,
) -> None:
    response = await test_client.get(url="/articles/no-such-article/comments")
    assert response.status_code == 404
