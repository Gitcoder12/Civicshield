"""CivicShield V2 — evidence-led civic food-safety workflow demo.

Run from the repository root:
    pip install streamlit pandas plotly scikit-learn
    streamlit run v2/app_v2.py

Important:
- Venue and area metrics are synthetic OSM-style fixtures, not live OSM extracts.
- Complaint classification is a small demonstration model, not a validated safety system.
- New reports remain pending until a human moderator approves them.
- State is held in Streamlit's session memory only; no database or real payment is configured.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


st.set_page_config(
    page_title="CivicShield V2 | Evidence-led food safety",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "2.0.0-demo"
FOOD_SAFETY_PORTAL = "https://foscos.fssai.gov.in/"
OSM_COPYRIGHT = "© OpenStreetMap contributors"

# These are synthetic records shaped around common OSM tags. They are not
# imported from OpenStreetMap and are not assertions about real businesses.
VENUE_FIXTURES = [
    {
        "venue_id": "fixture-osm-001",
        "name": "Sample Eatery — HITEC City",
        "area": "HITEC City",
        "lat": 17.4435,
        "lon": 78.3772,
        "cuisine": "Indian",
        "osm_tags": {"amenity": "restaurant", "cuisine": "indian"},
        "source_label": "Synthetic OSM-style fixture",
    },
    {
        "venue_id": "fixture-osm-002",
        "name": "Sample Cafe — Madhapur",
        "area": "Madhapur",
        "lat": 17.4483,
        "lon": 78.3915,
        "cuisine": "Cafe",
        "osm_tags": {"amenity": "cafe", "cuisine": "coffee_shop"},
        "source_label": "Synthetic OSM-style fixture",
    },
    {
        "venue_id": "fixture-osm-003",
        "name": "Sample Restaurant — Gachibowli",
        "area": "Gachibowli",
        "lat": 17.4401,
        "lon": 78.3489,
        "cuisine": "Multi-cuisine",
        "osm_tags": {"amenity": "restaurant", "cuisine": "multi_cuisine"},
        "source_label": "Synthetic OSM-style fixture",
    },
    {
        "venue_id": "fixture-osm-004",
        "name": "Sample Food Court — Kukatpally",
        "area": "Kukatpally",
        "lat": 17.4933,
        "lon": 78.3996,
        "cuisine": "Food court",
        "osm_tags": {"amenity": "food_court"},
        "source_label": "Synthetic OSM-style fixture",
    },
    {
        "venue_id": "fixture-osm-005",
        "name": "Sample Diner — Banjara Hills",
        "area": "Banjara Hills",
        "lat": 17.4156,
        "lon": 78.4347,
        "cuisine": "Indian",
        "osm_tags": {"amenity": "restaurant", "cuisine": "indian"},
        "source_label": "Synthetic OSM-style fixture",
    },
    {
        "venue_id": "fixture-osm-006",
        "name": "Sample Bakery — Secunderabad",
        "area": "Secunderabad",
        "lat": 17.4399,
        "lon": 78.4983,
        "cuisine": "Bakery",
        "osm_tags": {"shop": "bakery"},
        "source_label": "Synthetic OSM-style fixture",
    },
    {
        "venue_id": "fixture-osm-007",
        "name": "Sample Kitchen — Ameerpet",
        "area": "Ameerpet",
        "lat": 17.4375,
        "lon": 78.4483,
        "cuisine": "South Indian",
        "osm_tags": {"amenity": "restaurant", "cuisine": "south_indian"},
        "source_label": "Synthetic OSM-style fixture",
    },
    {
        "venue_id": "fixture-osm-008",
        "name": "Sample Bistro — Jubilee Hills",
        "area": "Jubilee Hills",
        "lat": 17.4310,
        "lon": 78.4070,
        "cuisine": "Multi-cuisine",
        "osm_tags": {"amenity": "restaurant", "cuisine": "multi_cuisine"},
        "source_label": "Synthetic OSM-style fixture",
    },
]

# Illustrative planning inputs only. The two indices are deliberately not
# represented as official population or business counts.
AREA_FIXTURES = [
    {"area": "HITEC City", "lat": 17.4435, "lon": 78.3772, "population_density_index": 92, "restaurant_supply_index": 61},
    {"area": "Madhapur", "lat": 17.4483, "lon": 78.3915, "population_density_index": 88, "restaurant_supply_index": 73},
    {"area": "Gachibowli", "lat": 17.4401, "lon": 78.3489, "population_density_index": 86, "restaurant_supply_index": 58},
    {"area": "Kukatpally", "lat": 17.4933, "lon": 78.3996, "population_density_index": 90, "restaurant_supply_index": 56},
    {"area": "Banjara Hills", "lat": 17.4156, "lon": 78.4347, "population_density_index": 74, "restaurant_supply_index": 82},
    {"area": "Secunderabad", "lat": 17.4399, "lon": 78.4983, "population_density_index": 83, "restaurant_supply_index": 62},
    {"area": "Ameerpet", "lat": 17.4375, "lon": 78.4483, "population_density_index": 87, "restaurant_supply_index": 54},
    {"area": "Jubilee Hills", "lat": 17.4310, "lon": 78.4070, "population_density_index": 70, "restaurant_supply_index": 79},
]

# Small, hand-written teaching corpus. This is not a validated or production
# training dataset. It exists to demonstrate the triage workflow end-to-end.
TRIAGE_TRAINING_EXAMPLES = [
    ("I found a hair in my food", "Hygiene"),
    ("The plate and spoon were dirty", "Hygiene"),
    ("There were cockroaches near the kitchen", "Hygiene"),
    ("The food smelled rotten and the counter was filthy", "Hygiene"),
    ("The restaurant staff served food with bare hands", "Hygiene"),
    ("The wash area was dirty and overflowing", "Hygiene"),
    ("I think the milk was mixed with something", "Adulteration"),
    ("The cooking oil looked reused and unusual", "Adulteration"),
    ("The spice powder may contain artificial colour", "Adulteration"),
    ("The product seal looked tampered with", "Adulteration"),
    ("There was a chemical smell in the drinking water", "Adulteration"),
    ("The packaged food label and contents did not match", "Adulteration"),
    ("The waiter shouted at customers", "Staff"),
    ("A worker handled cash and then touched food", "Staff"),
    ("The staff refused to wear gloves", "Staff"),
    ("The delivery person was rude to me", "Staff"),
    ("The employee ignored my hygiene complaint", "Staff"),
    ("The manager behaved aggressively", "Staff"),
    ("My order arrived late", "Other"),
    ("The bill had an incorrect amount", "Other"),
    ("The restaurant music was too loud", "Other"),
    ("The menu did not show prices clearly", "Other"),
    ("The online booking was not accepted", "Other"),
    ("The food was cold when it arrived", "Other"),
]


@st.cache_resource
def get_triage_model() -> Pipeline:
    """Train and cache the small demonstration TF-IDF + logistic model."""
    texts = [item[0] for item in TRIAGE_TRAINING_EXAMPLES]
    labels = [item[1] for item in TRIAGE_TRAINING_EXAMPLES]
    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    model.fit(texts, labels)
    return model


def initialize_session_state() -> None:
    """Initialize transient, per-session application state."""
    defaults = {
        "complaints": [],
        "corrective_actions": {},
        "partner_interest": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def classify_complaint(text: str) -> tuple[str, float]:
    model = get_triage_model()
    probabilities = model.predict_proba([text])[0]
    best_index = int(probabilities.argmax())
    category = str(model.classes_[best_index])
    confidence = float(probabilities[best_index])
    return category, confidence


def priority_for(category: str, confidence: float) -> str:
    # This flag only helps a human moderator prioritize review. It never
    # approves, rejects, publishes, or makes a legal finding.
    if category == "Adulteration" or confidence < 0.45:
        return "High — human review requested"
    return "Standard — human review required"


def area_summary() -> pd.DataFrame:
    areas = pd.DataFrame(AREA_FIXTURES)
    published = [
        report
        for report in st.session_state.complaints
        if report["status"] == "Approved"
    ]
    counts = pd.Series([report["area"] for report in published]).value_counts()
    areas["approved_report_count"] = areas["area"].map(counts).fillna(0).astype(int)
    areas["market_gap_index"] = (
        areas["population_density_index"] - areas["restaurant_supply_index"]
    ).clip(lower=0)
    return areas


def render_map(view: str) -> None:
    venues = pd.DataFrame(VENUE_FIXTURES)
    areas = area_summary()

    st.caption(
        "Map markers use synthetic OSM-style venue fixtures and illustrative area "
        "indices. The basemap is provided by OpenStreetMap; the displayed venue and "
        "planning data are not live OSM or official census data."
    )

    if view == "Citizen View — Approved report density":
        areas["plot_size"] = areas["approved_report_count"].clip(lower=1)
        fig = px.scatter_mapbox(
            areas,
            lat="lat",
            lon="lon",
            size="plot_size",
            color="approved_report_count",
            hover_name="area",
            hover_data={"approved_report_count": True, "lat": False, "lon": False, "plot_size": False},
            color_continuous_scale="Blues",
            size_max=34,
            zoom=10,
            center={"lat": 17.435, "lon": 78.43},
            mapbox_style="open-street-map",
            title="Approved citizen reports by area",
        )
        fig.update_traces(
            name="Approved reports",
            marker={"opacity": 0.82},
        )
        fig.add_trace(
            go.Scattermapbox(
                lat=venues["lat"],
                lon=venues["lon"],
                mode="markers",
                name="OSM-style venue fixtures",
                marker={"size": 9, "color": "#0f766e", "opacity": 0.85},
                text=venues["name"],
                customdata=venues[["area", "cuisine"]].to_numpy(),
                hovertemplate=(
                    "<b>%{text}</b><br>Area: %{customdata[0]}"
                    "<br>Type: %{customdata[1]}<br>Fixture data<extra></extra>"
                ),
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        st.metric(
            "Approved reports visible",
            int(areas["approved_report_count"].sum()),
            help="Only complaints explicitly approved by a human moderator are counted.",
        )
        st.info(
            "Pending and rejected complaints are excluded. With no approved reports, "
            "areas remain at zero; no report density is invented."
        )
    else:
        fig = px.scatter_mapbox(
            areas,
            lat="lat",
            lon="lon",
            size="market_gap_index",
            color="market_gap_index",
            hover_name="area",
            hover_data={
                "population_density_index": True,
                "restaurant_supply_index": True,
                "market_gap_index": True,
                "lat": False,
                "lon": False,
            },
            color_continuous_scale="OrRd",
            size_max=38,
            zoom=10,
            center={"lat": 17.435, "lon": 78.43},
            mapbox_style="open-street-map",
            title="Illustrative population-demand / restaurant-supply gap",
        )
        fig.add_trace(
            go.Scattermapbox(
                lat=venues["lat"],
                lon=venues["lon"],
                mode="markers",
                name="OSM-style venue fixtures",
                marker={"size": 8, "color": "#2563eb", "opacity": 0.75},
                text=venues["name"],
                hovertemplate="<b>%{text}</b><br>Demonstration venue fixture<extra></extra>",
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Market-gap index = illustrative population-density index minus "
            "illustrative restaurant-supply index, clipped at zero. Higher values "
            "identify candidate areas for further field research—not confirmed "
            "underserved markets."
        )


initialize_session_state()

st.title("🛡️ CivicShield V2")
st.subheader("Food safety, made more transparent.")
st.write(
    "An evidence-led civic technology prototype connecting citizen observations, "
    "human review, public visibility and restaurant response workflows."
)

with st.container(border=True):
    left, right = st.columns([3, 1])
    with left:
        st.markdown("**Evidence before claims. Human review before publication.**")
        st.write(
            "CivicShield V2 deliberately avoids synthetic food-safety scores and "
            "unverified claims of official FSSAI integration."
        )
    with right:
        st.link_button("Open official FoSCoS portal", FOOD_SAFETY_PORTAL, use_container_width=True)
    st.caption(
        "Demo status: synthetic venue fixtures · demonstration NLP model · "
        "session-only workflow · no official affiliation with FSSAI."
    )

citizen_tab, map_tab, admin_tab, owner_tab = st.tabs(
    ["Citizen Reporting", "Civic Map & Insights", "Admin Moderation", "Owner Portal"]
)

with citizen_tab:
    st.header("Submit a food-safety observation")
    st.write(
        "Describe what you observed. The NLP model suggests a category for the "
        "moderation team; it does not determine whether an allegation is true."
    )
    st.warning(
        "Do not include names, phone numbers, payment details or other personal "
        "information. This prototype is not an emergency reporting channel."
    )

    area_options = [item["area"] for item in AREA_FIXTURES]
    with st.form("citizen_complaint_form", clear_on_submit=True):
        selected_area = st.selectbox("Area", area_options)
        selected_venue = st.selectbox(
            "Venue (optional)",
            ["Not specified"] + [item["name"] for item in VENUE_FIXTURES],
        )
        complaint_text = st.text_area(
            "What happened?",
            placeholder="Example: I found a hair in my food.",
            max_chars=1200,
            height=140,
        )
        submitted = st.form_submit_button("Submit for human review", type="primary")

    if submitted:
        cleaned_text = complaint_text.strip()
        if len(cleaned_text) < 8:
            st.error("Please provide a little more detail (at least 8 characters).")
        else:
            category, confidence = classify_complaint(cleaned_text)
            complaint = {
                "id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "area": selected_area,
                "venue": None if selected_venue == "Not specified" else selected_venue,
                "text": cleaned_text,
                "category": category,
                "confidence": confidence,
                "priority": priority_for(category, confidence),
                "status": "Pending",
                "review_note": "",
            }
            st.session_state.complaints.append(complaint)
            st.success("Your observation is queued for human moderation. It is not public.")
            st.info(
                f"Suggested category: **{category}** · Model confidence: "
                f"**{confidence:.0%}** · Status: **Pending human review**"
            )

    st.markdown("#### How the AI triage works")
    st.write(
        "A TF-IDF text representation is passed to a Logistic Regression classifier. "
        "It suggests one of four categories: Hygiene, Adulteration, Staff or Other. "
        "The small training corpus is embedded for demonstration and is not a "
        "validated food-safety classifier."
    )

with map_tab:
    st.header("Civic map and area insights")
    selected_view = st.radio(
        "Choose a map view",
        [
            "Citizen View — Approved report density",
            "Brand View — Market gap analysis",
        ],
        horizontal=True,
    )
    render_map(selected_view)

    with st.expander("Inspect demonstration venue records"):
        venue_frame = pd.DataFrame(VENUE_FIXTURES)
        st.dataframe(
            venue_frame[["venue_id", "name", "area", "cuisine", "source_label"]],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "The venue records are synthetic OSM-style fixtures with illustrative "
            "OSM tag shapes. They do not have real OSM IDs and were not downloaded "
            "from OpenStreetMap."
        )

    with st.expander("Inspect area-planning fixture values"):
        st.dataframe(
            area_summary()[
                [
                    "area",
                    "population_density_index",
                    "restaurant_supply_index",
                    "market_gap_index",
                    "approved_report_count",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )
        st.caption(
            "All planning indices are synthetic examples. Replace them with "
            "documented, licensed sources before using this analysis for decisions."
        )

with admin_tab:
    st.header("Admin moderation queue")
    st.warning(
        "Demonstration-only moderation console. This tab has no authentication or "
        "role-based access control. Do not deploy it publicly as a real admin panel."
    )
    pending_reports = [
        report for report in st.session_state.complaints if report["status"] == "Pending"
    ]
    pending_reports.sort(
        key=lambda item: (
            item["priority"].startswith("High"),
            item["created_at"],
        ),
        reverse=True,
    )
    st.metric("Awaiting human review", len(pending_reports))

    if not pending_reports:
        st.info("No complaints are waiting for review.")
    for report in pending_reports:
        label = f"{report['category']} · {report['area']} · {report['priority']}"
        with st.expander(label, expanded=True):
            st.write(report["text"])
            st.caption(
                f"Suggested class: {report['category']} · "
                f"Confidence: {report['confidence']:.0%} · "
                f"Submitted: {report['created_at']}"
            )
            st.caption(
                "The model output is only a triage suggestion. The moderator must "
                "review the content and evidence independently."
            )
            note = st.text_input(
                "Moderator note (optional)",
                key=f"moderator_note_{report['id']}",
            )
            approve_col, reject_col = st.columns(2)
            with approve_col:
                if st.button(
                    "Approve for public map",
                    key=f"approve_{report['id']}",
                    type="primary",
                    use_container_width=True,
                ):
                    report["status"] = "Approved"
                    report["review_note"] = note.strip()
                    report["reviewed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                    st.rerun()
            with reject_col:
                if st.button(
                    "Reject",
                    key=f"reject_{report['id']}",
                    use_container_width=True,
                ):
                    report["status"] = "Rejected"
                    report["review_note"] = note.strip()
                    report["reviewed_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                    st.rerun()

    st.markdown("#### Moderation history")
    reviewed = [
        report
        for report in st.session_state.complaints
        if report["status"] in {"Approved", "Rejected"}
    ]
    if reviewed:
        history = pd.DataFrame(
            [
                {
                    "Area": item["area"],
                    "Category": item["category"],
                    "Status": item["status"],
                    "Reviewed at": item.get("reviewed_at", ""),
                    "Moderator note": item.get("review_note", ""),
                }
                for item in reviewed
            ]
        )
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        st.caption("No moderation decisions have been recorded in this session.")

with owner_tab:
    st.header("Restaurant owner portal")
    st.write(
        "A mock business workspace showing approved reports and a corrective-action "
        "response flow. It is not connected to real restaurant accounts."
    )
    st.warning(
        "Demo only: no owner authentication, durable evidence storage, subscription "
        "billing or payment processing is configured."
    )
    approved_reports = [
        report for report in st.session_state.complaints if report["status"] == "Approved"
    ]
    st.metric("Approved reports available to owners", len(approved_reports))

    if approved_reports:
        for report in approved_reports:
            with st.container(border=True):
                st.markdown(f"**{report['venue'] or 'Venue not specified'} — {report['area']}**")
                st.write(report["text"])
                st.caption(
                    f"Category: {report['category']} · "
                    f"Approved for public visibility"
                )
                uploaded = st.file_uploader(
                    "Upload corrective-action evidence (PDF, PNG or JPG)",
                    type=["pdf", "png", "jpg", "jpeg"],
                    key=f"corrective_upload_{report['id']}",
                )
                if st.button(
                    "Record corrective-action upload",
                    key=f"record_action_{report['id']}",
                    disabled=uploaded is None,
                ):
                    st.session_state.corrective_actions[report["id"]] = {
                        "file_name": uploaded.name,
                        "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    }
                    st.success(
                        f"Recorded {uploaded.name} for this session. "
                        "The file itself has not been durably stored."
                    )
                action = st.session_state.corrective_actions.get(report["id"])
                if action:
                    st.caption(
                        f"Session record: {action['file_name']} · {action['recorded_at']}"
                    )
    else:
        st.info(
            "No approved reports are available yet. Pending and rejected reports "
            "are intentionally hidden from this portal."
        )

    st.divider()
    st.subheader("Verified Partner")
    st.write(
        "Illustrative subscription concept: a restaurant profile, response workflow "
        "and verified-partner badge after an independent verification process."
    )
    st.button(
        "Upgrade to Verified Partner (₹499/mo)",
        key="mock_partner_upgrade",
        on_click=lambda: st.session_state.update({"partner_interest": True}),
    )
    if st.session_state.partner_interest:
        st.info(
            "Demo interest recorded in this session only. No payment was taken and "
            "no verified status was granted."
        )

st.divider()
with st.expander("Data provenance, privacy and prototype limitations"):
    st.markdown(
        f"""
        - **Venue fixtures:** synthetic OSM-style examples, not live OSM records.
        - **Area metrics:** illustrative indices, not official population or market data.
        - **Map tiles:** OpenStreetMap basemap; attribution: {OSM_COPYRIGHT}.
        - **FSSAI:** no FSSAI API is called. Use the official FoSCoS portal for manual verification.
        - **NLP:** a small demonstration TF-IDF + Logistic Regression model; not validated for operational or legal decisions.
        - **Moderation:** complaints are private and pending by default; only a human approval makes a complaint visible on the public map.
        - **Persistence:** all reports and actions live only in the current Streamlit session. Refreshes, restarts or session expiry may erase them.
        - **Security:** no production authentication, authorization, audit log, encryption-at-rest, malware scanning, durable storage or payment gateway is implemented.
        """
    )

st.caption(
    f"CivicShield V2 {APP_VERSION} · Academic prototype evolved into an evidence-led "
    "civic-tech workflow demonstration · Not an official FSSAI service."
)
