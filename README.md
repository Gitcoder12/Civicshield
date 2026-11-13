# CivicShield

**A browser-based food-safety transparency demo for Hyderabad.**

[![License](https://img.shields.io/badge/license-see%20LICENSE-lightgrey)](LICENSE)

CivicShield combines synthetic venue records, unverified community-report flows, and illustrative safety indicators in a single-page demonstration. All venue names, scores, license fields, and inspection records are placeholders—not real venue assessments or FSSAI records.

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
python -m pip install -r requirements-dev.txt
python backend_app.py
```

The backend binds to `127.0.0.1:5000` and uses a local JSON file for unverified community reports. Inspector submissions are rejected because the demo has no authority authentication. Citizen reports never change venue scores, license fields, or inspection records. Configure allowed browser origins with `CIVICSHIELD_CORS_ORIGINS`; debug mode is off by default.

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

This is a project demonstration, not an official FSSAI service. Every bundled venue record is synthetic; license statuses, scores, inspection details, and reports are placeholders. Citizen submissions are unverified allegations and are not proof of a violation. Inspector identity is not authenticated, and inspector submissions are disabled in the backend. The backend does not alter venue scores or official-looking fields from community reports. Confirm food-safety information with the appropriate official authority before making decisions. This demo does not replace inspection, laboratory testing, or emergency reporting.

## License

See [LICENSE](LICENSE).


## Development checks

```bash
python -m pip install -r requirements-dev.txt
ruff check backend_app.py tests
ruff format --check backend_app.py tests
pytest -q
```
