# CivicShield

**A browser-based food-safety transparency demo for Hyderabad.**

[![License](https://img.shields.io/badge/license-see%20LICENSE-lightgrey)](LICENSE)

CivicShield combines venue information, sample food-safety records, citizen-report flows, and public-facing safety indicators in a single-page demonstration.

## Features

- Browse bundled venue and restaurant records.
- View declared license-status fields and venue information.
- Explore area-level safety summaries.
- Submit a demo hygiene or food-safety report through the interface.
- Inspect sample audit and dish information.

## Quick Start

**Browser demo**

Open `index.html` in a modern browser. The main interface is self-contained and does not require a build step.

**Optional Flask API**

```bash
pip install flask flask-cors
python backend_app.py
```

The backend starts locally on port 5000.

## Tech Stack

HTML · CSS · Vanilla JavaScript · JSON · Python · Flask · Flask-CORS

## Project Structure

```text
Civicshield/
├── index.html       # Browser demo
├── hotels.json      # Bundled venue dataset
└── backend_app.py   # Optional Flask API
```

## Scope and Limitations

This is a project demonstration, not an official FSSAI service. Bundled license statuses, inspection details, venue ratings, and reports are not live government verification. Confirm food-safety information with the appropriate official authority before making decisions. The demo does not replace inspection, laboratory testing, or emergency reporting.

## License

See [LICENSE](LICENSE).

- [Agent instructions](AGENTS.md)
- [Agent skills](SKILLS.md)
- [Contributing](CONTRIBUTING.md)

- [Agent instructions](AGENTS.md)
- [Agent skills](SKILLS.md)
- [Contributing](CONTRIBUTING.md)

## Understanding the project

### In plain language

CivicShield is a demonstration of how people could browse example food-safety information about local venues and submit a community observation. The venue names and scores in the demo are examples, not official inspection results. A community report is an unverified observation, not proof that a business broke a rule.

### Technical and research view

The project combines a static HTML/CSS/JavaScript interface, JSON sample venue records and an optional Flask API. The API exposes venue lookup and community-report routes. The design must keep synthetic records, unverified community submissions and any future authenticated authority records separate. User-provided text is untrusted input and must be escaped before rendering. Community reports must not mutate official-looking scores, licence fields or inspection records.

The original feature list, setup instructions and limitations above remain authoritative. For future work, see [FEATURE_UPGRADE_PLAN.md](FEATURE_UPGRADE_PLAN.md), [ACTIVITY_LOG.md](ACTIVITY_LOG.md) and [CONTRIBUTING.md](CONTRIBUTING.md).
