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
