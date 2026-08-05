## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/154

**Issue title:** Health check DB probe passes a raw SQL string, which fails under SQLAlchemy 2.x

**Tier:** [x] Tier 1

**Selection reasoning:** This is a Tier 1 issue, which makes it a good fit since it's my first pathreview contribution and my first time working with a larger codebase. It's a self-contained API-layer bug where the main fix is wrapping a raw SQL query with text(), so the scope feels realistic for the Week 8–9 timeline. I don't have much prior Flask experience, but I'm comfortable with SQL and SQLAlchemy from a previous course project, which covers the core concepts needed for this fix.

**Problem summary:** The health check endpoint is supposed to verify that both the application and its database connection are working, but it currently passes a raw SQL string directly to SQLAlchemy. In SQLAlchemy 2.x, raw SQL strings need to be wrapped with text(), so the current implementation throws an error instead of confirming the database is reachable. As a result, the health check doesn't accurately reflect the application's status. The fix is to wrap the SQL query with text(), allowing it to execute correctly under SQLAlchemy 2.x and restoring the expected behavior. This issue is limited to the API layer, specifically the health check endpoint.

**Branch name:** fix/154-health-check-raw-sql

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger
## Week 8 — Reproduction & solution planning

**Reproduction commit link:** https://github.com/Manasvi-25/pathreview/commit/e6ebd4583ebeeb362563974c530821b3a225155e

**Reproduction summary:** I ran the app locally and hit the health check endpoint directly with `curl http://localhost:8000/health`. It confirmed the exact error described in issue #154: `Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`, causing the endpoint to report `"postgres": "unhealthy"` even though Postgres was actually running fine.

**PLAN.md link:** https://github.com/Manasvi-25/pathreview/blob/fix/154-health-check-raw-sql/PLAN.md

**Walkthrough video (recommended):** Not recorded.

**Blockers or open questions:** While setting up my local environment, I ran into unrelated pre-existing bugs — duplicate SQLAlchemy index definitions across three model files (`profile.py`, `ingested_source.py`, `review.py`) that blocked the app from booting at all, and some pre-commit lint/type errors in `health.py` itself. I fixed the index issues to get my environment running, but I want to make sure my actual PR for #154 stays scoped to just the raw SQL fix and doesn't get tangled with these unrelated issues.

## Week 9 — Solution building & PR submission

### Check-in 1 (mid-week)

**Current progress:** Implemented the core fix for issue #154 — wrapped the raw SQL string in `text()` in `api/routes/health.py`. Confirmed locally via curl that `/health` now reports `"postgres": "healthy"` instead of `"unhealthy"`.

**Next steps:** Writing a unit test for the health check endpoint, then running `make check` and `make test-unit` to confirm nothing else is broken. Plan to open a draft PR once tests pass.

**Blockers:** None currently, though the codebase has some pre-existing unrelated issues (duplicate model indexes from Week 8, and existing lint/type errors in `health.py`) I'll need to document as pre-existing rather than fix myself.

---

### Check-in 2 (end of week)

**PR link:** https://github.com/ascherj/pathreview/pull/910

**Branch:** fix/154-health-check-raw-sql

**What you built:** Fixed the health check endpoint's PostgreSQL probe, which was passing a raw SQL string to `db.execute()` — incompatible with SQLAlchemy 2.x. Wrapped the query in `sqlalchemy.text()` so the health check correctly reports database status.

**Tests added or updated:** Added `tests/unit/test_health.py` with 3 tests: one confirming postgres reports healthy when the query succeeds, a regression test confirming the query is passed as a `text()`-wrapped object rather than a raw string, and one confirming the endpoint correctly raises an HTTPException with status "unhealthy" when the database call fails.

**Manual verification steps:**
1. Start the app locally: `make run`
2. In a separate terminal, run: `curl http://localhost:8000/health`
3. Confirm the response includes `"postgres": "healthy"` (previously showed `"unhealthy"` due to the raw SQL bug)
4. Optionally, revert the `text()` wrapper locally and re-run step 2 to see the original error reproduced: `Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`

**Self-review confirmation:** [x] make check passes  [x] make test-unit passes

**Draft PR feedback received from:** none
