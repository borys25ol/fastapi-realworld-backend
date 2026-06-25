# CLAUDE.md — Project context for Claude Code

## What this is

FastAPI + PostgreSQL implementation of the [RealWorld / Conduit](https://github.com/gothinkster/realworld) spec, used as the target for an SDET practical assignment. The codebase has no frontend — all testing is through the API.

## How to run tests

Tests require Docker. There is no local Python 3.12 environment.

```bash
# Run a specific file
docker compose run --rm --entrypoint "" \
  -e SECRET_KEY=test-secret-key -e APP_ENV=test \
  -v "$(pwd)/tests:/app/tests:ro" api \
  pytest tests/api/routes/test_contract.py -v

# Run the full suite
docker compose run --rm --entrypoint "" \
  -e SECRET_KEY=test-secret-key -e APP_ENV=test \
  -v "$(pwd)/tests:/app/tests:ro" api \
  pytest tests/ -v
```

The `-v "$(pwd)/tests:/app/tests:ro"` mount is required because `tests/` is in `.dockerignore`. The `-e SECRET_KEY` and `-e APP_ENV=test` vars are required — the app won't start without them.

## Expected failures in the full suite

**~20 pre-existing tests fail with 429 when the full suite runs.** This is a known, documented product bug — not a regression introduced by new code. The `RateLimitingMiddleware` stores request counts in a plain Python dict on the middleware instance (`self.request_counts`). Because the `application` fixture is session-scoped (one FastAPI instance for the whole run), the counter accumulates across all tests. After ~100 requests from the shared `testserver` IP, every subsequent test gets 429.

- These tests all **pass in isolation**.
- Do not attempt to "fix" them by reordering tests or resetting state — the bug is in the middleware, not the tests.
- The fix is to back the counter with Redis and use a TTL-based key per IP.

## Known product bugs (do not accidentally fix)

1. **Stale slug after title update** (`conduit/infrastructure/repositories/article.py`).
   `get_by_slug` uses Python `or` instead of SQLAlchemy `|`:
   ```python
   # Bug: Python `or` — always discards the left side in SQLAlchemy 2.x
   query = select(Article).where(
       Article.slug == slug or Article.slug.contains(slug_unique_part)
   )
   ```
   `bool(BinaryExpression)` is `False` in SQLAlchemy 2.x, so the effective query is always `WHERE slug LIKE '%suffix%'`. Old slugs remain reachable after a title update. Documented in `test_stale_slug_accessible_after_title_update`.

2. **Rate limiter broken at scale** (`conduit/api/middlewares.py`).
   Per-instance dict means the limit is per-process (ineffective under multi-worker deployments) and accumulates across tests. See above.

3. **No max_length on username** — a 300-character username is accepted with 200. Documented in `test_username_max_length_not_enforced` (expected to fail with 422, currently passes with 200).

## Test file layout

```
tests/
  api/routes/
    test_registaration.py     # auth: register
    test_login.py             # auth: login
    test_user.py              # GET/PUT /user
    test_profile.py           # follow/unfollow, profile shape
    test_article.py           # CRUD, favorite/unfavorite
    test_article_filters.py   # tag/author/favorited filters, pagination
    test_article_integrity.py # cascade delete (comments, favorites)
    test_comments.py          # comment CRUD + permissions
    test_auth_permissions.py  # 403 paths
    test_validation.py        # 422 paths
    test_tags.py              # /tags endpoint
    test_health_check.py      # /health
    test_e2e_flows.py         # 4 full user-journey tests
    test_bug_probes.py        # 12 exploratory/boundary probes
    test_contract.py          # 17 response-shape tests vs Postman spec
  services/                   # service-layer unit tests (mock repos)
```

## Key test-writing rules

**Fixtures** — defined in `tests/conftest.py`. Key ones:
- `application` (session-scoped FastAPI app)
- `test_client` (unauthenticated `AsyncClient`)
- `authorized_test_client` (authenticated as `test_user`)
- `test_user`, `test_article`, `session`, `user_service`, `article_service`

Never call `create_app()` inside a test body — always accept the `application` fixture to keep all clients on the same DB session.

For a second authenticated user: register via `test_client.post("/users", ...)`, then open `AsyncClient(app=application, base_url="http://testserver/api", headers={"Authorization": f"Token {token}"})`.

**Vacuous loop guard** — if asserting inside `for item in body["items"]`, add `assert len(body["items"]) > 0` before the loop. An empty list silently skips all assertions.

**Feed tests** — `test_user` has no follows by default, so `/articles/feed` returns an empty list. Register a second user, publish an article as them, follow them first.

**JSON field names** — responses use camelCase aliases: `createdAt`, `updatedAt`, `tagList`, `favoritesCount`, `articlesCount`. Never assert the snake_case Python names.

**Contract tests** — only assert fields mandated by the official RealWorld Postman collection. `commentsCount` is an implementation extension; the spec returns `{"comments": [...]}` only.

## Pushing to GitHub

No SSH key or stored credentials. Use a PAT:

```bash
git push https://<PAT>@github.com/keerthisagar40/fastapi-realworld-backend.git master
```

Use `! git push https://<PAT>@...` in the Claude Code prompt to keep the token out of shell history.

## Skill

`/test-and-push` — invokes the step-by-step checklist for writing tests correctly and pushing safely.
