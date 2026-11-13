# CivicShield — Activity Log

**Repository:** https://github.com/Gitcoder12/Civicshield  
**Snapshot:** 2026-11-13

## Verified history

2026-11-13: PR #3 created to fix Flask root routing, declare Flask dependencies, default debug mode to off, add / and /hotels smoke tests, and add CI. Current PR-head backend check passed. PR is draft and unmerged: https://github.com/Gitcoder12/Civicshield/pull/3

## Log new work here

Append entries; do not rewrite history to make results look better.

| Date | Owner / agent | Issue or PR | Scope and files | Validation command / method | Result | Evidence and limitations |
|---|---|---|---|---|---|---|
| YYYY-MM-DD | name | #issue / #PR | exact paths | exact command | pass / fail / not run | link and caveats |

Record failed runs, regressions, reverted work and manual checks. Distinguish local tests, CI checks, simulated tests and production observations. Never call a draft PR merged or a green test production approval.

## Current known limitations

The current product is a demonstration using bundled sample records. Treat food-safety indicators as illustrative until their provenance, update cadence and verification authority are implemented.


## Additional verified security branch — 2026-11-13

**[PR #1: security/backend-hardening](https://github.com/Gitcoder12/Civicshield/pull/1)** was closed without merging at 2026-11-13 14:05:27 UTC. Its branch remains available at `security/backend-hardening` with head `10c136501e75ae1bc078845b97e2d42b4be25991`. The closed PR did not change the default branch.

The proposed branch replaces fabricated official-looking venue details with synthetic placeholders, labels scores and inspection fields as demo data, escapes user-supplied content, keeps community reports unverified, prevents reports from changing venue records, rejects unauthenticated inspector submissions, validates JSON payloads, writes local reports atomically, restricts CORS and binds the Flask API to loopback by default. It also adds regression tests and a CI workflow.

**Validation status at the recorded PR head:** all three backend CI jobs failed (Python 3.11, 3.12 and 3.13). The author stated that the local environment could not run the tests because Flask/Flask-CORS were unavailable. The PR body does not claim a passing test result. The Codex review comment said it found no major issues, but that review does not replace passing CI or browser verification.

**Preservation note:** the security PR branch has not been deleted or rewritten by this documentation change. The documentation PR only updates the activity record; it does not restore or remove product features, change venue data, or merge the security branch.

## Portfolio documentation rollout — 2026-11-13

- Documentation PR: https://github.com/Gitcoder12/Civicshield/pull/4
- Added project-specific activity log, prioritised feature plan, company-fit map, beginner/technical README guide and README quality checklist.
- Added or preserved contribution instructions and bounded agent/skills guidance as shown in the PR diff.
- Added a two-level explanation to the README: a plain-language overview and a technical/research view. Existing setup instructions and core feature descriptions were retained.
- Validation: documentation/source review only. No application runtime test or deployment is claimed by this documentation PR.
- Status: draft PR, not merged.
