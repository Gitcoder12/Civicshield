# AI Engineering Worklog

## 2026-11-13 — CivicShield demo hardening

### Completed
- Replaced the 114 browser-embedded venue records and 20 API venue records with synthetic demo names and placeholder license/inspection fields. Removed fabricated owner names, phone numbers, inspector identities, and official-looking FSSAI IDs from the browser dataset.
- Replaced the misleading live/verified/risk labels with explicit synthetic-demo wording.
- Escaped user-provided report notes and self-reported inspector details before HTML rendering.
- Made community allegations visibly unverified and stopped local reports from changing venue flags.
- Rebuilt the Flask backend with strict JSON shape, venue ID, checklist allowlist/type, report mode, and note-length validation.
- Rejected inspector submissions because the demo has no authority authentication.
- Prevented community reports from changing venue scores, license fields, inspection records, or adulteration flags.
- Added atomic JSON report writes, a process-local write lock, loopback-only binding, restricted configurable CORS, default-off debug mode, and basic response security headers.
- Added Flask backend regression tests, development dependencies, Ruff/pytest configuration, and a Python 3.11–3.13 CI workflow.
- Updated README, environment example, and gitignore.

### Validation status
- Tests authored in tests/test_backend.py; they have not yet been executed in a supported runtime.
- A GitHub Actions workflow was added in this PR, but the repository's default branch did not previously contain a workflow, so opening this PR did not trigger the newly added workflow.
- Local container execution was blocked because the container could not resolve GitHub and Flask/Flask-CORS are not installed in the available runtime.
- No passing CI or local test result is claimed.

### Remaining
- Run the new CI workflow after the workflow file is present on the default branch, or execute the test suite in an environment with requirements-dev.txt installed.
- The browser demo still stores reports in memory; only the optional Flask API persists unverified reports.
- The demo has no authentication, official FSSAI lookup, production database, rate limiting, or real inspection data.
- Review the front-end JavaScript changes in a browser before treating the UI as release-ready.
