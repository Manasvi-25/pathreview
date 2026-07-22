## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/154

**Issue title:** Health check DB probe passes a raw SQL string, which fails under SQLAlchemy 2.x

**Tier:** [x] Tier 1

**Selection reasoning:** This is a Tier 1 issue, which makes it a good fit since it's my first pathreview contribution and my first time working with a larger codebase. It's a self-contained API-layer bug where the main fix is wrapping a raw SQL query with text(), so the scope feels realistic for the Week 8–9 timeline. I don't have much prior Flask experience, but I'm comfortable with SQL and SQLAlchemy from a previous course project, which covers the core concepts needed for this fix.

**Problem summary:** The health check endpoint is supposed to verify that both the application and its database connection are working, but it currently passes a raw SQL string directly to SQLAlchemy. In SQLAlchemy 2.x, raw SQL strings need to be wrapped with text(), so the current implementation throws an error instead of confirming the database is reachable. As a result, the health check doesn't accurately reflect the application's status. The fix is to wrap the SQL query with text(), allowing it to execute correctly under SQLAlchemy 2.x and restoring the expected behavior. This issue is limited to the API layer, specifically the health check endpoint.

**Branch name:** fix/154-health-check-raw-sql

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger