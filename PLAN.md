## Solution plan

**Issue:** Health check DB probe passes a raw SQL string, which fails under SQLAlchemy 2.x — https://github.com/ascherj/pathreview/issues/154

### Understand
The health check endpoint (`GET /health`) is supposed to confirm the app and its dependencies (Postgres, Redis, vector DB) are reachable. The Postgres check calls `await db.execute("SELECT 1")` — a bare Python string. SQLAlchemy 2.x requires raw SQL to be wrapped in `text()` before execution; passing a plain string raises an error instead of running the query. Expected behavior: the probe runs `SELECT 1`, gets a result, and reports `"postgres": "healthy"`. Actual behavior: the probe throws `Textual SQL expression 'SELECT 1' should be explicitly declared as text('SELECT 1')`, caught by the surrounding `except` block and reported as `"postgres": "unhealthy"` — even though Postgres itself is running fine.

### Map
- `api/routes/health.py` — contains the `health_check()` function and the broken `await db.execute("SELECT 1")` line. This is the primary file needing a functional change.
- `tests/` — need to confirm exact path for health check tests, to add/update a test confirming the fix.

### Plan
1. Import `text` from `sqlalchemy` at the top of `api/routes/health.py`.
2. Wrap the raw SQL string: change `await db.execute("SELECT 1")` to `await db.execute(text("SELECT 1"))`.
3. Restart the app locally and re-run `curl http://localhost:8000/health` to confirm `"postgres": "healthy"` instead of `"unhealthy"`.
4. Locate or write a unit/integration test for the health check endpoint asserting a 200 response and `"postgres": "healthy"` when the DB is reachable.
5. Run the full test suite to confirm nothing else breaks from this change.

### Inputs & outputs
- Input: an active async DB session (`db`) injected via FastAPI's `Depends(get_db)`.
- Output before fix: `503 Service Unavailable` with `"postgres": "unhealthy"` due to the uncaught SQLAlchemy error.
- Output after fix: `200 OK` with `"postgres": "healthy"` when Postgres is reachable, or accurate `"unhealthy"` only when Postgres is genuinely down.

### Risks & unknowns
- Need to confirm there are no other raw SQL string calls elsewhere in the codebase using the same unwrapped pattern.
- Not yet sure where existing health check tests live, or if any exist — need to check `tests/` structure before writing a new one.
- The repo has a broader pattern of pre-existing bugs (I found and fixed duplicate SQLAlchemy index definitions across three model files, and hit unrelated pre-commit lint/type errors in `health.py` itself) — want to make sure my fix stays scoped to #154 and doesn't get tangled with unrelated fixes when I open my PR.

### Edge cases
- Postgres genuinely unreachable (e.g. Docker container stopped) — health check should still correctly report `"unhealthy"`.
- Query executes but returns unexpected data — shouldn't happen with `SELECT 1`, but worth confirming the check only cares about successful execution.
- Concurrent requests to `/health` — each should get an independent DB session with no shared-state issues.
