"""
Contract tests derived from the official RealWorld Postman collection
(postman/Conduit.postman_collection.json).

Each test verifies that a response:
  - contains the required top-level wrapper key
  - contains all required fields the spec mandates
  - uses the correct types (int for counts, list for arrays)
  - formats timestamps as ISO 8601 with decimal seconds and a UTC suffix,
    matching the regex the Postman suite uses:
      ^\\d{4,}-[01]\\d-[0-3]\\dT[0-2]\\d:[0-5]\\d:[0-5]\\d\\.\\d+(?:[+-]\\d{2}:\\d{2}|Z)$
"""
import re

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from conduit.dtos.domain.article import ArticleDTO
from conduit.dtos.domain.user import UserDTO
from conduit.interfaces.services.user import IUserService
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils import create_another_test_user

# Postman ISO 8601 regex (requires decimal seconds — e.g. ".123456Z")
ISO_8601 = re.compile(
    r"^\d{4,}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+"
    r"(?:[+-][0-2]\d:[0-5]\d|Z)$"
)


def assert_iso8601(value: str, field: str) -> None:
    assert ISO_8601.match(value), (
        f"'{field}' value {value!r} does not match ISO 8601 with decimal seconds"
    )


def assert_user_shape(user: dict) -> None:
    for field in ("email", "username", "bio", "image", "token"):
        assert field in user, f"user missing '{field}'"


def assert_article_shape(article: dict) -> None:
    for field in ("title", "slug", "body", "description",
                  "tagList", "author", "favorited", "favoritesCount",
                  "createdAt", "updatedAt"):
        assert field in article, f"article missing '{field}'"
    assert isinstance(article["tagList"], list), "tagList must be a list"
    assert isinstance(article["favoritesCount"], int), "favoritesCount must be int"
    assert_iso8601(article["createdAt"], "article.createdAt")
    assert_iso8601(article["updatedAt"], "article.updatedAt")
    assert_author_shape(article["author"])


def assert_author_shape(author: dict) -> None:
    for field in ("username", "bio", "image", "following"):
        assert field in author, f"author missing '{field}'"
    assert isinstance(author["following"], bool), "author.following must be bool"


def assert_comment_shape(comment: dict) -> None:
    for field in ("id", "body", "createdAt", "updatedAt", "author"):
        assert field in comment, f"comment missing '{field}'"
    assert isinstance(comment["id"], int), "comment.id must be int"
    assert_iso8601(comment["createdAt"], "comment.createdAt")
    assert_iso8601(comment["updatedAt"], "comment.updatedAt")
    assert_author_shape(comment["author"])


def assert_profile_shape(profile: dict) -> None:
    for field in ("username", "bio", "image", "following"):
        assert field in profile, f"profile missing '{field}'"
    assert isinstance(profile["following"], bool), "profile.following must be bool"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_contract_register_response_shape(test_client: AsyncClient) -> None:
    response = await test_client.post(
        "/users",
        json={"user": {"username": "contract-reg", "email": "contract-reg@example.com", "password": "password"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert "user" in body
    assert_user_shape(body["user"])


@pytest.mark.anyio
async def test_contract_login_response_shape(
    test_client: AsyncClient, test_user: UserDTO
) -> None:
    response = await test_client.post(
        "/users/login",
        json={"user": {"email": "test@gmail.com", "password": "password"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert "user" in body
    assert_user_shape(body["user"])


@pytest.mark.anyio
async def test_contract_current_user_response_shape(
    authorized_test_client: AsyncClient,
) -> None:
    response = await authorized_test_client.get("/user")
    assert response.status_code == 200
    body = response.json()
    assert "user" in body
    assert_user_shape(body["user"])


@pytest.mark.anyio
async def test_contract_update_user_response_shape(
    authorized_test_client: AsyncClient,
) -> None:
    response = await authorized_test_client.put(
        "/user", json={"user": {"bio": "Updated bio for contract test"}}
    )
    assert response.status_code == 200
    body = response.json()
    assert "user" in body
    assert_user_shape(body["user"])


# ---------------------------------------------------------------------------
# Articles
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_contract_article_list_response_shape(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.get("/articles")
    assert response.status_code == 200
    body = response.json()
    assert "articles" in body
    assert "articlesCount" in body
    assert isinstance(body["articlesCount"], int), "articlesCount must be int"
    assert isinstance(body["articles"], list)
    assert len(body["articles"]) > 0, "need at least one article to validate shape"
    for article in body["articles"]:
        assert_article_shape(article)


@pytest.mark.anyio
async def test_contract_create_article_response_shape(
    authorized_test_client: AsyncClient,
) -> None:
    response = await authorized_test_client.post(
        "/articles",
        json={"article": {
            "title": "Contract Test Article",
            "description": "Description for contract test purposes",
            "body": "Body content for contract test purposes",
            "tagList": ["contract", "test"],
        }},
    )
    assert response.status_code == 200
    body = response.json()
    assert "article" in body
    assert_article_shape(body["article"])


@pytest.mark.anyio
async def test_contract_get_article_response_shape(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.get(f"/articles/{test_article.slug}")
    assert response.status_code == 200
    body = response.json()
    assert "article" in body
    assert_article_shape(body["article"])


@pytest.mark.anyio
async def test_contract_update_article_response_shape(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.put(
        f"/articles/{test_article.slug}",
        json={"article": {"body": "Updated body for contract shape test purpose"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert "article" in body
    assert_article_shape(body["article"])


@pytest.mark.anyio
async def test_contract_favorite_article_response_shape(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.post(
        f"/articles/{test_article.slug}/favorite"
    )
    assert response.status_code == 200
    body = response.json()
    assert "article" in body
    assert_article_shape(body["article"])
    assert body["article"]["favorited"] is True


@pytest.mark.anyio
async def test_contract_unfavorite_article_response_shape(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    await authorized_test_client.post(f"/articles/{test_article.slug}/favorite")
    response = await authorized_test_client.delete(
        f"/articles/{test_article.slug}/favorite"
    )
    assert response.status_code == 200
    body = response.json()
    assert "article" in body
    assert_article_shape(body["article"])
    assert body["article"]["favorited"] is False


@pytest.mark.anyio
async def test_contract_feed_response_shape(
    authorized_test_client: AsyncClient,
    application: FastAPI,
    test_client: AsyncClient,
) -> None:
    # Register a second user, publish an article as them, follow them so the
    # feed is non-empty — without this the article-shape assertions never execute.
    resp = await test_client.post(
        "/users",
        json={"user": {
            "username": "feed-author-ct",
            "email": "feed-author-ct@example.com",
            "password": "password",
        }},
    )
    assert resp.status_code == 200
    author_token = resp.json()["user"]["token"]

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers={"Authorization": f"Token {author_token}"},
    ) as author_client:
        resp = await author_client.post(
            "/articles",
            json={"article": {
                "title": "Feed Author Article",
                "description": "Article for feed contract test",
                "body": "Body of the feed author article for contract test",
                "tagList": [],
            }},
        )
        assert resp.status_code == 200

    await authorized_test_client.post("/profiles/feed-author-ct/follow")

    response = await authorized_test_client.get("/articles/feed")
    assert response.status_code == 200
    body = response.json()
    assert "articles" in body
    assert "articlesCount" in body
    assert isinstance(body["articlesCount"], int)
    assert isinstance(body["articles"], list)
    assert len(body["articles"]) > 0, "feed must be non-empty to validate article shape"
    for article in body["articles"]:
        assert_article_shape(article)


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_contract_create_comment_response_shape(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.post(
        f"/articles/{test_article.slug}/comments",
        json={"comment": {"body": "A contract test comment"}},
    )
    assert response.status_code == 200
    body = response.json()
    assert "comment" in body
    assert_comment_shape(body["comment"])


@pytest.mark.anyio
async def test_contract_list_comments_response_shape(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    await authorized_test_client.post(
        f"/articles/{test_article.slug}/comments",
        json={"comment": {"body": "Comment for list shape test"}},
    )
    response = await authorized_test_client.get(
        f"/articles/{test_article.slug}/comments"
    )
    assert response.status_code == 200
    body = response.json()
    # The spec returns {"comments": [...]} — commentsCount is an implementation
    # extension and is intentionally not asserted here.
    assert "comments" in body
    assert isinstance(body["comments"], list)
    assert len(body["comments"]) > 0, "need at least one comment to validate shape"
    for comment in body["comments"]:
        assert_comment_shape(comment)


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_contract_get_profile_response_shape(
    authorized_test_client: AsyncClient,
    test_user: UserDTO,
    session: AsyncSession,
    user_service: IUserService,
) -> None:
    other = await create_another_test_user(session=session, user_service=user_service)
    response = await authorized_test_client.get(f"/profiles/{other.username}")
    assert response.status_code == 200
    body = response.json()
    assert "profile" in body
    assert_profile_shape(body["profile"])


@pytest.mark.anyio
async def test_contract_follow_profile_response_shape(
    authorized_test_client: AsyncClient,
    session: AsyncSession,
    user_service: IUserService,
) -> None:
    other = await create_another_test_user(session=session, user_service=user_service)
    response = await authorized_test_client.post(f"/profiles/{other.username}/follow")
    assert response.status_code == 200
    body = response.json()
    assert "profile" in body
    assert_profile_shape(body["profile"])
    assert body["profile"]["following"] is True


@pytest.mark.anyio
async def test_contract_unfollow_profile_response_shape(
    authorized_test_client: AsyncClient,
    session: AsyncSession,
    user_service: IUserService,
) -> None:
    other = await create_another_test_user(session=session, user_service=user_service)
    await authorized_test_client.post(f"/profiles/{other.username}/follow")
    response = await authorized_test_client.delete(f"/profiles/{other.username}/follow")
    assert response.status_code == 200
    body = response.json()
    assert "profile" in body
    assert_profile_shape(body["profile"])
    assert body["profile"]["following"] is False


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_contract_tags_response_shape(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.get("/tags")
    assert response.status_code == 200
    body = response.json()
    assert "tags" in body
    assert isinstance(body["tags"], list), "tags must be a list"
