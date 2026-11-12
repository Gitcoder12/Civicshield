# CivicShield

**Food Safety, Made Public.**  
An academic civic-technology project exploring how food-safety information, citizen observations and inspector workflows could be brought into one transparent experience.

> **Project identity:** M.Tech CSE · Amity University Hyderabad · March–April 2026  
> **Student authors:** D. Satvik and C. Ajay  
> **Academic supervisor:** Dr. Ratnanjali Tiwari

CivicShield began as an academic project and browser demonstration for Hyderabad. Its central idea is to make food-safety information easier to discover, give citizens a structured way to report observations, and provide a workflow through which authorized reviewers can assess and respond to those reports.

This repository now preserves two distinct generations:

- **V1 — academic demonstration:** the original browser interface and its bundled sample dataset.
- **V2 — evidence-led prototype:** a separate Streamlit application exploring source provenance, NLP-assisted triage, human moderation and a mock restaurant-owner workflow.

V1 is intentionally preserved. V2 does not replace or silently rewrite the V1 interface or dataset.

---

## Project at a glance

| Area | Description |
|---|---|
| Domain | Food-safety transparency and civic technology |
| Original geography | Hyderabad, Telangana, India |
| Academic method | ICEDIP: Identify, Collect, Evaluate, Design, Implement, Promote |
| Original interface | HTML, CSS and JavaScript |
| Original backend experiment | Python and Flask |
| V2 interface | Streamlit |
| V2 geospatial visualization | Plotly maps |
| V2 complaint triage | TF-IDF + Logistic Regression (demonstration model) |
| V2 review policy | Human approval required before public display |
| V2 business concept | Mock B2B restaurant-owner portal |

## Quick links

- [V1 browser application](index.html)
- [V1 bundled dataset](hotels.json)
- [V1 Flask backend](backend_app.py)
- [Official FoSCoS portal](https://foscos.fssai.gov.in/)
- [OpenStreetMap](https://www.openstreetmap.org/)

**V2 source:** `v2/app_v2.py` on the `v2-ultra-cooked` development branch.

## Academic origin and project context

CivicShield was developed as an M.Tech CSE academic project at Amity University Hyderabad by D. Satvik and C. Ajay under the guidance of Dr. Ratnanjali Tiwari. The project was also presented in the university's World Creativity and Innovation Day 2026 activity.

The original academic framing identified three connected challenges:

1. Citizens may not easily find or interpret food-establishment licensing and inspection information.
2. Citizen observations about hygiene or suspected adulteration may not have a structured, visible reporting workflow.
3. Public information, inspection processes and restaurant-level information can be fragmented across different systems.

The academic concept proposed a single civic interface with venue discovery, FSSAI-related information, citizen reporting, inspector audit workflows, dish/venue information and area-level visualization.

### ICEDIP methodology

| Phase | Meaning | CivicShield application |
|---|---|---|
| **Identify** | Understand the problem | Identify the food-safety information and reporting gap experienced by citizens. |
| **Collect** | Gather relevant material | Review available food-safety information, venue records, user needs and project references. |
| **Evaluate** | Examine existing options | Compare existing discovery and official information channels to identify the project's intended gap. |
| **Design** | Plan the solution | Define the interface, data fields, reporting flow and proposed system architecture. |
| **Implement** | Build the prototype | Create the browser-based V1 and explore backend workflows. |
| **Promote** | Present and communicate | Prepare academic presentation material and explain possible future expansion. |

The poster and presentation materials contain the original academic project's claims, scope, proposed design and reported demonstration figures. Those figures should be read as **project-reported academic material**, not as independently audited government data or proof of a deployed city-wide service.

---

# V1 — Original academic browser demonstration

V1 is preserved as the original single-page browser project.

### Run V1

No frontend build system is required for the static page. Open `index.html` in a modern browser, or serve the repository root locally:

```bash
python -m http.server 8000
```

Then visit:

`http://localhost:8000`

### V1 files

```text
Civicshield/
├── index.html       # Original browser-based academic interface
├── hotels.json      # Bundled demonstration venue records
├── backend_app.py   # Optional Flask API experiment
└── README.md
```

The bundled venue data is a project demonstration dataset. License status, inspection details, ratings and reports in this dataset must not be interpreted as current official FSSAI verification.

### Original concept features

- Venue and restaurant discovery.
- FSSAI-related license information display.
- Citizen hygiene and food-safety reporting concept.
- Inspector audit workflow concept.
- Dish and restaurant information.
- Area-level safety visualization.
- Restaurant-chain and branch comparison concept.

The presence of a feature in the academic concept or presentation does not necessarily mean that a live government integration, production workflow or persistent backend was completed.

---

# V2 — Evidence-led civic technology prototype

V2 is a separate Streamlit application. Its design direction is to replace unsupported claims with clear provenance, explicit review states and reproducible workflows.

### Run V2 locally

From the repository root:

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install streamlit pandas plotly scikit-learn
streamlit run v2/app_v2.py
```

The application opens in the local Streamlit browser session. The interactive OpenStreetMap basemap requires internet connectivity.

## Engineering maturity & data provenance pivot

During the transition from the original concept to V2, we separated the desired product capability from what could be responsibly verified through available integrations. The team could not establish a documented, supported public API suitable for automatic FSSAI license verification in this prototype; therefore, V2 does not pretend to perform a live government lookup.

**No public FSSAI/FoSCoS API integration is implemented in this prototype.** We therefore do not claim that CivicShield performs automatic, live license verification. The application links users to the official [FoSCoS portal](https://foscos.fssai.gov.in/) for manual verification.

V2 uses structured **synthetic OSM-style venue fixtures** to demonstrate geospatial data handling and map interaction. The records follow familiar OpenStreetMap tag conventions such as `amenity`, `shop` and `cuisine`, but they are not downloaded OSM records and do not have real OSM object IDs.

The area-level population-density and restaurant-supply values are illustrative planning indices. They are not official census statistics, verified restaurant counts, market research or food-safety measurements.

This distinction is intentional:

- A real place name is not proof of a valid food license.
- An OSM venue record is not a hygiene inspection.
- A citizen complaint is an allegation until reviewed.
- A visualization is not evidence unless its source, method and limitations are disclosed.

A future live-data integration should use a documented, licensed OSM extract or supported Overpass workflow with attribution, source timestamps, object identifiers and refresh/error handling. Any official licensing integration must use an authorized interface or permitted data source.

## Geospatial map: Citizen View and Brand View

V2 includes a Plotly map with two separate analytical views.

### Citizen View — approved report density

- Displays area-level counts of complaints approved by a human moderator.
- Pending and rejected reports are excluded.
- If no report has been approved, the area remains at zero; the map does not invent report density.
- Venue markers are explicitly identified as synthetic OSM-style fixtures.

### Brand View — market-gap exploration

- Compares an illustrative population-density index with an illustrative restaurant-supply index.
- Calculates a simple gap proxy: population-demand index minus restaurant-supply index, clipped at zero.
- Highlights candidate areas that may merit additional market research.

The market-gap view is a demonstration of an analytical method, not a validated commercial opportunity assessment. Replace its fixture inputs with sourced and dated data before making investment, expansion or site-selection decisions.

## AI NLP triage: TF-IDF + Logistic Regression

The prototype trains a small Scikit-Learn pipeline using a hand-written demonstration corpus:

1. **TF-IDF Vectorizer** converts complaint text into weighted word and phrase features.
2. **Logistic Regression** predicts one of four suggested categories:
   - `Hygiene`
   - `Adulteration`
   - `Staff`
   - `Other`
3. The predicted category and model confidence are displayed as triage hints.
4. Adulteration suggestions, explicit hazard phrases (for example suspected poisoning, chemicals or foreign objects), and low-confidence predictions receive a high-priority review flag. These are conservative triage cues, not medical or legal findings.

The embedded corpus is deliberately small and is not representative of all languages, dialects, reporting styles, food types or real-world incidents. The classifier has not been validated for operational accuracy. Its confidence is not the probability that a complaint is true.

The model is an administrative aid, not an investigator, regulator, legal decision-maker or autonomous enforcement system.

## Human-in-the-Loop (HITL) safety

**AI does not publish complaints.**

Every new complaint enters a pending moderation queue. The NLP model may suggest a category and a review priority, but it cannot approve, reject, substantiate or publicly expose a report.

The moderation workflow is:

```text
Citizen submits observation
          |
          v
TF-IDF + Logistic Regression
          |
          v
Suggested category + review priority
          |
          v
Pending human moderation
       /       \
      /         \
  Approve      Reject
     |            |
     v            v
Public map     Not published
and owner
portal
```

Only a moderator's explicit approval makes a complaint visible in the public Citizen View and Owner Portal. Rejected and pending reports remain excluded.

This is a prototype safety design, not a complete legal-compliance solution. A production system would additionally require authenticated moderator roles, evidence review, audit logs, appeal/correction processes, privacy controls, abuse prevention and defined retention policies.

## B2B monetization strategy

The product concept has two sides:

### Citizen experience — free

Citizens can discover available information and submit observations without a subscription. Public visibility is governed by human review and data-provenance rules.

### Restaurant-owner experience — SaaS concept

The mock Owner Portal demonstrates how an establishment could:

- View complaints approved for public visibility.
- Submit corrective-action evidence.
- Track its response history.
- Explore a proposed Verified Partner subscription.

The interface includes a **₹499/month** mock upgrade button. It does not charge money, create a subscription, verify a restaurant or grant a real partner badge. Those capabilities would require identity checks, payment processing, contractual terms, security and an auditable verification process.

The intention is to explore a sustainable B2B service without charging citizens to access public-interest information.

## Current V2 implementation boundaries

The current V2 application is a local demonstration, not a production SaaS service.

| Capability | Current state |
|---|---|
| Streamlit interface | Implemented in V2 app |
| Plotly map | Uses synthetic venue and area fixtures |
| Citizen report submission | Session-only demonstration |
| NLP triage | Small embedded TF-IDF + Logistic Regression model |
| Human moderation | Session-only approve/reject flow |
| Public map visibility | Approved reports only |
| Owner Portal | Mock interface |
| Corrective-action upload | File selection and session-only filename record; no durable storage |
| Verified Partner | Mock interest button; no payment |
| FSSAI integration | Official portal link; no API integration |
| Persistent database | Not implemented |
| Authentication / RBAC | Not implemented |
| Production deployment | Not established |

Streamlit session state can be lost when a session expires, restarts or is otherwise reset. Do not use this build to submit real sensitive complaints or upload confidential evidence.

## Production-readiness roadmap

Before V2 is used outside a controlled demonstration, the following work is required:

1. **Data ingestion:** integrate a permitted OSM data source and documented demographic datasets; preserve identifiers, licenses, timestamps and provenance.
2. **Official verification:** investigate authorized FoSCoS integration options; retain manual official verification links until an approved interface exists.
3. **Durable storage:** implement a database, migrations, backups and retention controls.
4. **Privacy and security:** add authentication, role-based access, encryption, secure uploads, malware scanning, rate limiting and audit logging.
5. **Moderation operations:** define moderator permissions, review standards, evidence handling, dispute and correction workflows.
6. **Model evaluation:** build a representative, consent-aware, multilingual labelled dataset; measure per-class precision/recall, confusion matrix, calibration and drift; retain human decision authority.
7. **Owner verification:** establish a documented business identity and evidence-review process before displaying a verified-partner claim.
8. **Payments:** integrate a compliant payment provider only after pricing, terms, refunds, invoices and subscription controls are defined.
9. **Deployment:** add automated tests, monitoring, incident response, backups and tested restoration procedures.

## Responsible-use statement

CivicShield is an academic and engineering prototype. It is not an official FSSAI service, does not conduct food inspections, and does not certify that a restaurant is safe or unsafe. The prototype's demo classifier, synthetic data, market-gap indices and user-submitted observations must not be treated as verified facts.

For official licensing questions, use the [FoSCoS portal](https://foscos.fssai.gov.in/). For immediate health or food-poisoning concerns, contact the appropriate local health authorities or emergency services rather than relying on this prototype.

## Contributing and development

V1 is retained as an academic reference. V2 development is isolated on the `v2-ultra-cooked` branch until its implementation and verification gates are reviewed.

For changes:

- Preserve V1 files unless a separately approved task explicitly requires otherwise.
- Keep source references and data provenance visible.
- Never introduce fabricated safety scores, fake official verification or unlabelled synthetic records.
- Do not auto-publish AI-classified complaints.
- Document setup steps and verify that examples run before claiming they work.

## License

See [LICENSE](LICENSE).
