# Contributing to CivicShield

Thanks for helping improve this project. The aim is small, reviewable contributions with reproducible evidence.

## Start here

1. Read README.md and FEATURE_UPGRADE_PLAN.md.
2. Check open issues and pull requests to avoid duplicate work.
3. Pick one bounded task and describe the intended result before editing.
4. Create a branch from the current default branch.
5. Add or update tests and user documentation with the code change.
6. Open a pull request with the exact validation commands and results.

## Good contribution areas

1. Replace sample-only venue data with a documented, provenance-aware data adapter without implying official approval.
2. Validate report payloads, venue identifiers and API errors; add tests for malformed and duplicate submissions.
3. Define moderation, abuse prevention, audit trail and retention policies before public citizen submissions.
4. Add accessible filters, mobile UI smoke tests and a reproducible local demo.

## Pull request checklist

- [ ] Scope is limited to one issue or work package.
- [ ] Existing behavior and API compatibility were considered.
- [ ] Tests cover the change and at least one failure case.
- [ ] Documentation and examples match actual behavior.
- [ ] Data sources, assumptions and limitations are stated.
- [ ] No secrets, private user data or unlicensed datasets are included.
- [ ] Failed tests and uncompleted checks are reported honestly.

## AI agent rules

Agents may inspect, test, document and propose changes. They must not claim a test passed unless they ran it or have a linked CI result. Work on feature branches, keep diffs minimal, preserve data provenance and ask for human review before any merge or deployment.
