# CivicShield

**Food safety, made public.**

CivicShield is an academic civic-tech project exploring how people can find food-safety information, report concerns and follow a transparent review process.

Built as an M.Tech CSE project at **Amity University Hyderabad** by **D. Satvik and C. Ajay**, under the guidance of **Dr. Ratnanjali Tiwari**.

CivicShield was developed with the intention of showcasing it during the university's **World Creativity and Innovation Day 2026** activity.

## Features

- Restaurant discovery using OpenStreetMap data.
- Citizen food-safety reports.
- NLP-assisted complaint categorization.
- Human approval before reports appear publicly.
- Map-based views of restaurants and approved reports.
- Mock restaurant-owner portal.

## Versions

- **V1:** Original browser-based academic demo built with HTML, CSS and JavaScript.
- **V2:** Streamlit prototype with live OpenStreetMap data, complaint triage and human moderation.

V1 is preserved in the repository. V2 is developed separately on the `v2-ultra-cooked` branch.

## Run V1

From the repository folder:

```bash
python -m http.server 8000
```

Open http://localhost:8000.

## Run V2

Clone the V2 branch:

```bash
git clone -b v2-ultra-cooked https://github.com/Gitcoder12/Civicshield.git
cd Civicshield
python -m venv .venv
```

Activate the environment, then install and run:

```bash
pip install -r requirements.txt
streamlit run v2/app_v2.py
```

The V2 map requires an internet connection.

## Data and limitations

- Restaurant locations come from OpenStreetMap. OSM listings do not prove that a restaurant is licensed or safe.
- CivicShield does not have a live FSSAI/FoSCoS API integration. Use the [official FoSCoS portal](https://foscos.fssai.gov.in/) for license-related checks.
- The NLP classifier is a small demonstration model, not validated for real-world decisions.
- Reports and moderation state are stored only for the active Streamlit session.
- The owner portal and subscription option are mock features. No payments are processed.
- CivicShield is an academic prototype, not an official inspection or certification service.

OpenStreetMap data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright).

## Tests

Install development dependencies and run:

```bash
pip install -r requirements-dev.txt
ruff check v2 tests
python -m compileall -q v2 tests
pytest -q
```

GitHub Actions runs the checks on Python 3.11, 3.12 and 3.13.

## Project structure

```text
Civicshield/
├── index.html
├── hotels.json
├── backend_app.py
├── v2/
│   ├── app_v2.py
│   └── osm_data.py
├── tests/
└── README.md
```

## License

See [LICENSE](LICENSE).
