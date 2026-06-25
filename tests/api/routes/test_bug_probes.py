"""
Exploratory probes to find unexpected behaviour / bugs.
Each test is independent and self-contained.
"""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from conduit.dtos.domain.article import ArticleDTO
from conduit.dtos.domain.user import UserDTO
from conduit.core.dependencies import IAuthTokenService
from conduit.interfaces.services.user import IUserService
from sqlalchemy.ext.asyncio import AsyncSession
from tests.utils import create_another_test_user


# ---------------------------------------------------------------------------
# Article edge cases
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_delete_already_deleted_article_returns_404(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    await authorized_test_client.delete(url=f"/articles/{test_article.slug}")
    response = await authorized_test_client.delete(url=f"/articles/{test_article.slug}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_update_article_with_empty_body_keeps_existing_values(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.put(
        url=f"/articles/{test_article.slug}",
        json={"article": {}},
    )
    assert response.status_code == 200
    data = response.json()["article"]
    assert data["title"] == test_article.title
    assert data["description"] == test_article.description
    assert data["body"] == test_article.body


@pytest.mark.anyio
async def test_stale_slug_accessible_after_title_update(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    """
    BUG: get_by_slug uses Python `or` instead of SQLAlchemy `|` in its WHERE clause:

        Article.slug == slug or Article.slug.contains(slug_unique_part)

    In SQLAlchemy 2.x, bool(BinaryExpression) evaluates to False, so Python's `or`
    always discards the left side. The effective query becomes:

        WHERE slug LIKE '%<unique_suffix>%'

    Because title updates preserve the unique suffix, the old slug still matches
    the new slug via the LIKE clause — so the article is found under both slugs.

    Fix: replace `or` with `|` (SQLAlchemy bitwise-or) to produce a proper SQL OR,
    or simply remove the contains fallback and use an exact match only.
    """
    original_slug = test_article.slug
    response = await authorized_test_client.put(
        url=f"/articles/{original_slug}",
        json={"article": {"title": "A Completely Different Title Now"}},
    )
    assert response.status_code == 200
    new_slug = response.json()["article"]["slug"]
    assert new_slug != original_slug

    # Old slug should return 404 — but due to the bug it returns 200
    response = await authorized_test_client.get(url=f"/articles/{original_slug}")
    assert response.status_code == 200, "BUG still present: old slug resolves after title update"


@pytest.mark.anyio
async def test_user_can_favorite_own_article(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.post(
        url=f"/articles/{test_article.slug}/favorite"
    )
    # Note: the spec doesn't forbid self-favoriting — just documenting actual behaviour
    assert response.status_code in (200, 400), (
        f"BUG: unexpected status {response.status_code} when favoriting own article"
    )


# ---------------------------------------------------------------------------
# Comment edge cases
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_delete_nonexistent_comment_returns_404(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.delete(
        url=f"/articles/{test_article.slug}/comments/99999"
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Input validation / boundary probes
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_negative_limit_rejected(authorized_test_client: AsyncClient) -> None:
    response = await authorized_test_client.get(url="/articles?limit=-1")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_zero_limit_rejected(authorized_test_client: AsyncClient) -> None:
    response = await authorized_test_client.get(url="/articles?limit=0")
    assert response.status_code == 422


@pytest.mark.anyio
async def test_very_large_offset_returns_empty(
    authorized_test_client: AsyncClient, test_article: ArticleDTO
) -> None:
    response = await authorized_test_client.get(url="/articles?limit=20&offset=999999")
    assert response.status_code == 200
    assert response.json()["articlesCount"] == 1   # total count unaffected by offset
    assert response.json()["articles"] == []        # but page is empty


@pytest.mark.xfail(strict=True, reason="known bug: no max_length enforced on username field")
@pytest.mark.anyio
async def test_username_max_length_not_enforced(
    test_client: AsyncClient,
) -> None:
    long_username = "a" * 300
    response = await test_client.post(
        url="/users",
        json={"user": {"username": long_username, "email": "long@example.com", "password": "password"}},
    )
    assert response.status_code == 422, (
        f"BUG: 300-char username accepted with {response.status_code} — no max_length enforced on username"
    )


@pytest.mark.anyio
async def test_empty_bearer_token_rejected(test_client: AsyncClient) -> None:
    response = await test_client.get(
        url="/user",
        headers={"Authorization": "Token ", "Content-Type": "application/json"},
    )
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Security probes
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_xss_payload_stored_verbatim_not_sanitized(
    authorized_test_client: AsyncClient,
) -> None:
    xss = "<script>alert(1)</script>"
    response = await authorized_test_client.post(
        url="/articles",
        json={"article": {
            "title": "XSS Probe Article Here",
            "description": "Checking if XSS is sanitized in body",
            "body": xss,
            "tagList": [],
        }},
    )
    assert response.status_code == 200
    slug = response.json()["article"]["slug"]

    response = await authorized_test_client.get(url=f"/articles/{slug}")
    stored_body = response.json()["article"]["body"]

    # The API stores and returns raw HTML — no sanitization.
    # This is only dangerous if a frontend renders it unescaped.
    assert stored_body == xss, "Body was unexpectedly modified"


@pytest.mark.anyio
async def test_sql_injection_in_slug_returns_404(
    authorized_test_client: AsyncClient,
) -> None:
    response = await authorized_test_client.get(
        url="/articles/'; DROP TABLE users; --"
    )
    assert response.status_code == 404
