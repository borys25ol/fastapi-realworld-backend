"""
End-to-end tests that simulate real user journeys through the API without
relying on pre-seeded fixtures. Each test registers and acts as a real client.
"""
import pytest
from httpx import AsyncClient
from fastapi import FastAPI


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Token {token}", "Content-Type": "application/json"}


async def _register(client: AsyncClient, username: str, email: str) -> str:
    """Register a new user and return their JWT token."""
    response = await client.post(
        "/users",
        json={"user": {"username": username, "email": email, "password": "password"}},
    )
    assert response.status_code == 200, response.text
    return response.json()["user"]["token"]


@pytest.mark.anyio
async def test_full_article_lifecycle(
    application: FastAPI, test_client: AsyncClient
) -> None:
    """Register → create article → comment → delete article → all gone."""
    token = await _register(test_client, "alice-lifecycle", "alice-lifecycle@example.com")

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers=_auth_headers(token),
    ) as client:
        # Create article
        resp = await client.post(
            "/articles",
            json={
                "article": {
                    "title": "Alice's Article",
                    "description": "A test article",
                    "body": "Hello world",
                    "tagList": ["e2e"],
                }
            },
        )
        assert resp.status_code == 200
        slug = resp.json()["article"]["slug"]

        # Add a comment
        resp = await client.post(
            f"/articles/{slug}/comments",
            json={"comment": {"body": "First comment!"}},
        )
        assert resp.status_code == 200

        # Verify comment appears in list
        resp = await client.get(f"/articles/{slug}/comments")
        assert resp.json()["commentsCount"] == 1

        # Delete the article
        resp = await client.delete(f"/articles/{slug}")
        assert resp.status_code == 204

        # Article is gone
        resp = await client.get(f"/articles/{slug}")
        assert resp.status_code == 404

        # Comments are also gone
        resp = await client.get(f"/articles/{slug}/comments")
        assert resp.status_code == 404


@pytest.mark.anyio
async def test_follow_and_feed_flow(
    application: FastAPI, test_client: AsyncClient
) -> None:
    """Alice follows Bob → Bob publishes → Alice's feed shows Bob's article."""
    alice_token = await _register(test_client, "alice-feed", "alice-feed@example.com")
    bob_token = await _register(test_client, "bob-feed", "bob-feed@example.com")

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers=_auth_headers(bob_token),
    ) as bob:
        resp = await bob.post(
            "/articles",
            json={
                "article": {
                    "title": "Bob's Post",
                    "description": "Written by Bob for the feed test",
                    "body": "Bob writes here for everyone to read",
                    "tagList": [],
                }
            },
        )
        assert resp.status_code == 200
        bob_slug = resp.json()["article"]["slug"]

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers=_auth_headers(alice_token),
    ) as alice:
        # Alice follows Bob
        resp = await alice.post("/profiles/bob-feed/follow")
        assert resp.status_code == 200
        assert resp.json()["profile"]["following"] is True

        # Alice's feed contains Bob's article
        resp = await alice.get("/articles/feed")
        assert resp.status_code == 200
        slugs = [a["slug"] for a in resp.json()["articles"]]
        assert bob_slug in slugs

        # Alice unfollows Bob
        resp = await alice.delete("/profiles/bob-feed/follow")
        assert resp.status_code == 200
        assert resp.json()["profile"]["following"] is False

        # Feed is now empty
        resp = await alice.get("/articles/feed")
        assert resp.json()["articlesCount"] == 0


@pytest.mark.anyio
async def test_favorite_count_flow(
    application: FastAPI, test_client: AsyncClient
) -> None:
    """Favorite increments count; unfavorite decrements it back."""
    token = await _register(test_client, "alice-fav", "alice-fav@example.com")

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers=_auth_headers(token),
    ) as client:
        resp = await client.post(
            "/articles",
            json={
                "article": {
                    "title": "Favourable Article",
                    "description": "An article worth favouriting",
                    "body": "This is the body of the favourable article",
                    "tagList": [],
                }
            },
        )
        assert resp.status_code == 200
        slug = resp.json()["article"]["slug"]
        assert resp.json()["article"]["favoritesCount"] == 0

        # Favorite the article
        resp = await client.post(f"/articles/{slug}/favorite")
        assert resp.status_code == 200
        assert resp.json()["article"]["favoritesCount"] == 1
        assert resp.json()["article"]["favorited"] is True

        # Unfavorite
        resp = await client.delete(f"/articles/{slug}/favorite")
        assert resp.status_code == 200
        assert resp.json()["article"]["favoritesCount"] == 0
        assert resp.json()["article"]["favorited"] is False


@pytest.mark.anyio
async def test_cross_user_comment_permissions(
    application: FastAPI, test_client: AsyncClient
) -> None:
    """Alice publishes; Bob comments; Alice cannot delete Bob's comment; Bob can."""
    alice_token = await _register(test_client, "alice-perm", "alice-perm@example.com")
    bob_token = await _register(test_client, "bob-perm", "bob-perm@example.com")

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers=_auth_headers(alice_token),
    ) as alice:
        resp = await alice.post(
            "/articles",
            json={
                "article": {
                    "title": "Alice Perm Article",
                    "description": "Alice writes about permissions",
                    "body": "This article tests cross-user comment permissions",
                    "tagList": [],
                }
            },
        )
        assert resp.status_code == 200
        slug = resp.json()["article"]["slug"]

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers=_auth_headers(bob_token),
    ) as bob:
        resp = await bob.post(
            f"/articles/{slug}/comments",
            json={"comment": {"body": "Bob's thoughts"}},
        )
        assert resp.status_code == 200
        comment_id = resp.json()["comment"]["id"]

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers=_auth_headers(alice_token),
    ) as alice:
        # Alice cannot delete Bob's comment
        resp = await alice.delete(f"/articles/{slug}/comments/{comment_id}")
        assert resp.status_code == 403

    async with AsyncClient(
        app=application,
        base_url="http://testserver/api",
        headers=_auth_headers(bob_token),
    ) as bob:
        # Bob can delete his own comment
        resp = await bob.delete(f"/articles/{slug}/comments/{comment_id}")
        assert resp.status_code == 204
