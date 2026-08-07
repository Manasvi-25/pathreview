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

Pre-existing test failures (unrelated to this PR): Running make test-unit shows 53 failing tests across the suite (378 passing). These failures live entirely in files unrelated to this fix — test_bias_detector.py, test_review_service.py, test_pii_scrubber.py, test_resume_parser.py, test_skill_extractor.py, test_readme_parser.py, test_structural_chunker.py, test_tech_detector.py, and others — several of which correspond to separately tracked open issues in the repo (e.g. #146, #147, #148, #151). My changes are scoped entirely to api/routes/health.py and tests/unit/test_health.py; all 3 tests in test_health.py pass, and none of the pre-existing failures touch the health check code path

## Week 10 — Iteration & reflection

### Reviewer feedback


**Feedback received:** [ ] Yes  [x] No — still awaiting review

**Summary of feedback:** No review arrived by the end of the week.

**How you responded:** NA

---

### Reflection

**What was harder than you expected?**

I think the hardest part wasn't fixing the bug. It was figuring out which bug I was actually supposed to fix. 
First I had to get the health check endpoint working on my laptop, and that itself took some time because I was running into WSL setup issues. Once I finally got it running, I expected the error to point straight to the problem, but it didn't. The project already had a bunch of other bugs and failing tests, so every time something crashed, I had to stop and figure out if it was something that already existed or if it was actually related to issue #154.
So I basically had to go through everything one step at a time. I'd trigger the health check, read the stack trace, compare it with the assignment description, and then check what make check and make test-unit were already failing on before I changed anything. That helped me separate the existing issues from the one I actually needed to fix, which was the SQLAlchemy 2.x raw SQL problem.
I honestly thought finding the bug would be the easy part and that I'd spend most of my time coding the fix. It ended up being the opposite. Most of the time went into understanding the project, narrowing down the actual issue, and making sure I wasn't chasing bugs that weren't part of the assignment.


**What did you learn about working in a large codebase?**

Working in a larger codebase was really different from working on my own projects. Normally, I know where everything is because I wrote it, so if something breaks I usually have a good idea of where to start. Here, I couldn't just open the file that seemed related to the bug and make a change.

I first had to understand how the health check endpoint fit into the rest of the application, what functions called it, and how SQLAlchemy was being used in other parts of the project. I also had to trace how api/routes/health.py worked and confirm that the db.execute() call was actually the source of issue #154 instead of just another symptom. The repository also had a separate pre-existing bug with duplicate SQLAlchemy index definitions causing a DuplicateTableError during startup, so I had to rule that out before I could be confident I was fixing the right issue.

Something else I learned was that reading code is just as important as writing it. Before making any changes, I looked through the existing tests, especially tests/unit/test_health.py, the project documentation including CONTRIBUTING.md, and the code around the health check so I could understand why it was written that way. That gave me a lot more confidence that my fix was solving the right problem instead of accidentally introducing a new one.

Overall, I learned that working in a large codebase is a lot less about immediately writing code and a lot more about understanding how everything connects before making even a small change.


**How did AI tools help — and where did they fall short?**

AI was really helpful for understanding unfamiliar parts of the codebase and explaining the SQLAlchemy 2.x changes that caused the bug. It helped me understand why the old db.execute() call was failing and pointed me toward wrapping the raw SQL in text(), which matched the correct SQLAlchemy 2.x approach. Once I had identified the actual issue, AI also helped me think through a possible fix and come up with test cases to verify that the health check still worked correctly.

Where it fell short was during the investigation. It couldn't tell me which errors were actually related to issue #154 and which were caused by other pre-existing bugs in the repository, so I still had to read stack traces, compare failing tests, and verify everything myself. It also wasn't much help with the Windows/WSL setup problems I ran into, since those depended on my local environment rather than the code itself.

I also realized that even when the code AI generated worked, it didn't always match the project's existing coding style or conventions. I still had to read through the surrounding code, understand how the rest of the project handled similar cases, and adjust the solution so it fit naturally into the codebase. AI definitely made the process faster and helped me learn unfamiliar concepts more quickly, but it couldn't replace the actual debugging, investigation, and decision-making that went into finding and fixing the right bug.


**What would you do differently if you started over?**

If I started over, I'd first make sure my WSL environment was completely set up and working before touching any code. I ended up spending much more time dealing with environment issues than I expected, including WSL configuration problems, virtual environment issues, and rebuilding my setup after my laptop was reformatted. Having all of that working from the start would have made the debugging process much smoother and let me focus on the actual assignment sooner.

I'd also spend more time reproducing and fully understanding the bug before trying to fix it. Early on, I was eager to jump into the code, but I realized that understanding why the bug was happening was just as important as knowing where it was happening. I also spent time figuring out whether the DuplicateTableError caused by duplicate SQLAlchemy index definitions was related to issue #154 before confirming it was a separate, pre-existing bug. Being more systematic about ruling out unrelated errors first would have saved me time and made the investigation more efficient.

Finally, I'd use AI more intentionally. It was great for explaining concepts like the SQLAlchemy 2.x changes and helping me understand unfamiliar code, but I learned that I shouldn't accept its suggestions without verifying them against the project's documentation, existing code, and coding conventions. Spending a little more time understanding the codebase before making changes would have helped me avoid unnecessary rework later.

**What are you most proud of from this module?**

I'm most proud that I didn't give up when the project became more complicated than I expected. What seemed like a straightforward bug fix turned into debugging environment issues, sorting through pre-existing failures, and understanding a codebase I had never seen before. Even when things weren't working, I kept narrowing down the problem instead of making random changes until I was confident I had identified the actual cause. By the end, I felt much more comfortable reading unfamiliar code, tracing bugs through the application, and making changes carefully instead of relying on guesswork. That confidence is probably the biggest thing I gained from this module.