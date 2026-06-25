# SDET Assignment — Test Coverage Summary

### Why this implementation

FastAPI + PostgreSQL backend implementing the full RealWorld / Conduit spec. I chose it because the stack (async Python, SQLAlchemy, pytest-anyio) is one I'm comfortable owning end-to-end, the app has clean layering (routes → services → repositories) that makes failure modes easy to reason about, and it had some existing test coverage

---

### What was tested

#### API tests (`tests/api/routes/`)

| File | Coverage |
|---|---|
| `test_comments.py` | Create comment; response shape; list with count; unauthenticated list; delete own; deleted comment disappears; can't delete another user's comment → 403; comment on non-existent article → 404 |
| `test_contract.py` | Response shape / field / type / timestamp-format assertions derived from the official RealWorld Postman collection; covers auth, articles, comments, profiles, tags (17 tests) |

#### E2E flows (`tests/api/routes/test_e2e_flows.py`)

| Flow | Description |
|---|---|
| `test_full_article_lifecycle` | Register → create article → comment → verify comment → delete article → 404 → comments 404 |
| `test_follow_and_feed_flow` | Alice follows Bob → Bob's article in feed → unfollow → feed empty |
| `test_favorite_count_flow` | Favorite → `favoritesCount` increments → unfavorite → back to 0 |
| `test_cross_user_comment_permissions` | Alice publishes → Bob comments → Alice can't delete Bob's comment (403) → Bob can (204) |


#### Boundary / probe tests (`tests/api/routes/test_bug_probes.py`)

12 tests covering: delete already-deleted article, stale slug after title update, negative/zero limit → 422, very large offset returns empty page, XSS payload stored verbatim, SQL injection in slug → 404, empty bearer token → 403, self-favoriting behaviour.

#### AI testing patterns (`tests/ai/`)

13 tests against a hypothetical `ArticleSummarizer` service demonstrating: schema validation, property assertions, semantic similarity, PII detection, token-limit enforcement, graceful LLM failure, golden-set regression. No real LLM is called — everything is mocked.

**CI:** GitHub Actions workflow (`.github/workflows/tests.yaml`) runs the full suite on every push/PR using a postgres:16 service container. Result: **123 passed, 1 xfailed**.

**Developer tooling:**
- `CLAUDE.md` — auto-loaded by Claude Code every session; documents the docker test command, the 20 expected rate-limiter failures, the three known product bugs, and fixture rules so no context is lost between sessions.
- `/test-and-push` skill (`.claude/commands/test-and-push.md`) — invokable checklist that enforces correct test-writing patterns (vacuous loop guards, no non-spec contract assertions, multi-user setup, fixture rules) and the push workflow before any code reaches the remote.

---

### How I used AI agents

**Tool:** Claude Code (claude-sonnet-4-6 via the CLI).

**Where it helped:** Surveying the existing test surface and identifying gaps; generating scaffolds for `test_comments.py` and `test_e2e_flows.py` in line with existing fixture conventions.

**Where I overrode it:** The first draft of `test_user_cannot_delete_another_users_comment` called `create_app()` inside the test body, bypassing test isolation. I rewrote it to use the session-scoped `application` fixture. I also rejected the agent's suggestion to stub the second user's token inside a fixture, preferring `auth_token_service` directly in the test — simpler and makes the dependency explicit.

---

### Bugs found

- **No max_length on username** — 300-char username accepted with 200 OK (`test_username_max_length_not_enforced`, marked `xfail`).
- **No max_length on comment body** — 10,000-char comment accepted with 200 OK.
- **Stale slug after title update** — `get_by_slug` uses Python `or` instead of SQLAlchemy `|`, so the WHERE clause reduces to `LIKE '%suffix%'`. Old slugs remain accessible after a title change. Fix: replace `or` with `|`. Confirmed by `test_stale_slug_accessible_after_title_update`.
- **Rate limiter broken at scale** — `RateLimitingMiddleware` stores counts in a per-instance Python dict. In multi-worker deployments the effective limit is `N × 100 req/min` per IP. Fix: back with Redis using a TTL-keyed counter. Test workaround: ceiling raised to 100,000 in conftest to prevent false 429s in CI.

---

### What I'd do with more time

- Feed pagination — `limit`/`offset` on `/articles/feed` not yet tested
- Unicode edge cases in slugs — non-ASCII titles, emoji, RTL characters
- Increase coverage for all areas above 85%

---

### Bonus — Testing non-deterministic AI features

Generative model outputs can't be tested with `assert output == expected`. The strategy:

1. **Schema validation** — response shape is deterministic even if content isn't. Assert required fields, types, and bounds on every call.
2. **Property assertions** — invariants that must hold regardless of content: summary shorter than source, no PII in output, sentiment score between 0–1. Model-agnostic and run in CI.
3. **Semantic similarity** — Jaccard word-overlap or sentence-transformer embeddings with a floor threshold. Detects drift to off-topic output, not word-for-word matching.
4. **Golden-set regression** — curated `(input, min_score)` pairs labelled by domain experts. Track scores over time in LangSmith / W&B / RAGAS — a gradual decline matters as much as a sudden drop.
5. **LLM-as-judge** — use a stronger model to evaluate complex outputs against a rubric. Expensive; reserve for pre-release eval runs, not every CI push.

**Practical rules:** mock the LLM in unit/integration tests; use real calls only in scheduled eval runs; assert on the prompt the mock received (not just the output); test graceful degradation when the LLM times out or rate-limits; track token cost and latency as metrics.
