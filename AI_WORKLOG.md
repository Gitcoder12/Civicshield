# AI Engineering Worklog

## Audit record

- Date: 2026-11-13
- Audited base: `main` at `a59dba179407968dc1c79db6b2d7a5b4597282d3`
- Review branch: `fix/backend-static-root-and-smoke-tests`
- Related pull request: [#3](https://github.com/Gitcoder12/Civicshield/pull/3)
- Classification: active browser demo with an experimental Flask API
- Scope inspected: repository tree, README, data file, Flask routes, audit router, open issue #2, and open PRs #3 and #4.

## Confirmed findings

### P1 - Report submission can mutate official-looking venue state

In `backend_app.py`, `POST /submit_report` accepts a caller-controlled `mode`, including `inspector`, without authentication or authorization. It also sets `adulteration_flag` in `hotels.json` and updates `base_score` using community-submitted checklist data. This conflicts with open issue #2, which explicitly requires community reports not to modify venue scores, license status, inspection records, or adulteration flags. The endpoint must remain untrusted-report intake until a real authority identity and authorization model exists.

### P1 - Unsafe deployment defaults

The module applies unrestricted `CORS(app)`, has no authentication or rate limiting, and starts Flask with `debug=True` when executed directly. These settings are not appropriate for a publicly reachable service. Do not deploy this API publicly in its current state.

### P1 - Browser route mismatch on main

The Flask app configures `static_folder="../frontend"` and serves `../frontend/index.html`, but the committed tree contains `index.html` at repository root and no `frontend/` directory. Open PR #3 changes this path and adds smoke tests.

### P2 - Persistence and input validation

JSON writes to `hotels.json` and `reports.json` are direct, non-atomic read-modify-write operations with no concurrency control. Request fields and checklist values are not validated against a strict schema; notes length and accepted report modes are not bounded.

### P1 - Data provenance is unverified

`hotels.json` contains official-looking FSSAI identifiers, license statuses, inspection dates, safety scores, and venue records. Their provenance was not established in this pass. Preserve the dataset unchanged. Do not describe these fields as official or verified until every record has traceable evidence.

## Structure and maturity

- Main contains 9 tracked files, including a large single-page `index.html`, `backend_app.py`, `hotels.json`, environment example, license, contribution guide, and audit router.
- Main contains no test files, dependency manifest, or GitHub Actions workflow.
- Open issue #2 defines a safer browser/API integration contract.
- Open PR #3 adds a route correction, requirements, smoke tests, and CI. Its GitHub Actions run completed successfully on the PR head; this does not validate the current main branch or resolve the report-integrity issues above.
- Open PR #4 is documentation-focused and remains draft.

## Verification

- Repository tree and selected source/data files inspected through GitHub.
- No local tests were run in this audit.
- PR #3 Actions run: [43417119116](https://github.com/Gitcoder12/Civicshield/actions/runs/43417119116), completed successfully.
- Independent review of the current PR #3 head: NOT PERFORMED; no review submission was present when checked.
- Runtime data provenance and external FSSAI verification: NOT PERFORMED.

## Next actions

1. Remove inspector mode from public report submission until authenticated authorization exists.
2. Ensure citizen reports are append-only unverified observations and cannot mutate venue/license/inspection state or official scores.
3. Restrict CORS, disable debug by default, add rate limiting and request-size limits before any network exposure.
4. Add schema validation, atomic persistence, and concurrent-write tests.
5. Trace the provenance of every official-looking data field without replacing the existing dataset.
6. Re-run tests and CI on the exact updated PR head, then obtain an independent review.
