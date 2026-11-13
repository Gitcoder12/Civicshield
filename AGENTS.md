# Agent Instructions — CivicShield

Read README.md, CONTRIBUTING.md, FEATURE_UPGRADE_PLAN.md and ACTIVITY_LOG.md before editing.

- Preserve useful venue browsing, filters, report workflows and demo UX unless a specific issue requires a change.
- Never invent official venue records, FSSAI IDs, inspector identities, owner contacts or inspection outcomes.
- Keep synthetic demo values clearly labelled and community submissions visibly unverified.
- Escape untrusted text before rendering and validate API input.
- Community reports must not modify official-looking venue scores, licence fields or inspection records without a separately authenticated authority workflow.
- Add tests for validation, XSS, API permissions, persistence and frontend behavior.
- Do not claim tests passed unless CI/local output proves it.
- Work on a feature branch; open a PR. Human approval is required for merge and deployment.
