# Test and Push

Before pushing any code, follow these steps in order. Do not skip any step.

## Step 1 — Review what changed

Run `git diff HEAD` and `git status` to understand what files changed. For each changed file, identify:
- Is this a new feature, bug fix, or refactor?
- Which existing tests cover this code path?
- What new tests are needed?

## Step 2 — Write tests (if needed)

If new or modified code is not already covered, write tests before running anything. Follow these rules for this project:

**Fixtures and setup**
- Use the existing fixtures from `tests/conftest.py`: `test_user`, `test_article`, `authorized_test_client`, `test_client`, `session`, `user_service`, `article_service`, `application`.
- Never create a new `FastAPI` app inside a test body — always use the session-scoped `application` fixture to keep all clients pointed at the same test database.
- For multi-user tests, use `create_another_test_user` from `tests/utils.py` or register via `test_client.post("/users", ...)` and create an `AsyncClient(app=application, ...)` for that user's token.

**Avoid vacuous tests**
- If a test asserts something inside a `for` loop (e.g. `for article in body["articles"]`), add `assert len(body["articles"]) > 0` before the loop. A test that passes because the list is empty has proven nothing.
- For feed tests: the test user starts with no follows, so the feed is empty by default. Register a second user, have them publish an article, and follow them before hitting `/articles/feed`.

**Contract tests**
- Only assert fields that the official RealWorld Postman collection mandates. `commentsCount` is an implementation extension — do not assert it as a contract requirement. The spec returns `{"comments": [...]}` only.
- Check both the POST and DELETE variants of favorite/unfavorite and follow/unfollow — both return a response body.

**Pydantic aliases**
- JSON responses use camelCase aliases: `createdAt`, `updatedAt`, `tagList`, `favoritesCount`, `articlesCount`. Never assert the snake_case field names.

**Timestamp format**
- Timestamps follow ISO 8601 with decimal seconds: `YYYY-MM-DDTHH:MM:SS.ffffffZ`. Use the compiled regex in `test_contract.py` to validate format, not just presence.

## Step 3 — Run the tests

Run only the tests related to the changed code first, then the full suite:

```
# Targeted run (fast feedback)
docker compose run --rm --entrypoint "" -e SECRET_KEY=test-secret-key -e APP_ENV=test \
  -v "$(pwd)/tests:/app/tests:ro" api \
  pytest tests/api/routes/test_<relevant_file>.py -v

# Full suite (catch regressions)
docker compose run --rm --entrypoint "" -e SECRET_KEY=test-secret-key -e APP_ENV=test \
  -v "$(pwd)/tests:/app/tests:ro" api \
  pytest tests/ -v
```

## Step 4 — Inspect results

- **All new tests must pass.**
- **The 20 pre-existing failures caused by the rate limiter are expected** — they fail with 429 when the full suite runs because `RateLimitingMiddleware` accumulates counts across tests in the session-scoped app. They all pass in isolation. Do not count these as regressions.
- If any *other* test that was passing before is now failing, investigate before proceeding.

## Step 5 — Commit

Stage only the relevant files (never `git add .` blindly — avoid accidentally staging `.env`, credentials, or large binaries):

```
git add <specific files>
git commit -m "<concise message describing why, not what>"
```

## Step 6 — Push

Push using the PAT-authenticated URL (the repo has no stored credentials or SSH key):

```
git push https://<PAT>@github.com/keerthisagar40/fastapi-realworld-backend.git master
```

Remind the user to use `! git push https://<PAT>@...` in the Claude Code prompt so the token stays out of shell history where possible.
