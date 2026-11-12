"""CivicShield V2 — evidence-led civic food-safety workflow demo.

Run from the repository root:
    pip install -r requirements.txt
    streamlit run v2/app_v2.py

Important:
- Restaurant records are fetched from OpenStreetMap through the Overpass API and cached for six hours.
- Population-density data is not yet connected, so the app does not claim a verified market-gap result.
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

try:
    from v2.osm_data import HYDERABAD_BBOX, OSM_CACHE_SECONDS, fetch_osm_restaurants
except ModuleNotFoundError:
    # Streamlit may put the script directory, rather than repository root, on sys.path.
    from osm_data import HYDERABAD_BBOX, OSM_CACHE_SECONDS, fetch_osm_restaurants


st.set_page_config(
    page_title="CivicShield V2 | Evidence-led food safety",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "2.1.0-osm"
FOOD_SAFETY_PORTAL = "https://foscos.fssai.gov.in/"
OSM_COPYRIGHT_URL = "https://www.openstreetmap.org/copyright"

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


HIGH_RISK_TERMS = (
    "food poisoning",
    "poison",
    "chemical",
    "glass",
    "metal fragment",
    "metal piece",
    "wire",
    "mould",
    "mold",
    "worm",
    "allergic reaction",
    "allergy",
    "hospital",
    "severe illness",
    "blood",
    "contaminated",
    "adulterated",
    "foreign object",
)


def priority_for(category: str, confidence: float, complaint_text: str) -> str:
    # These are conservative review cues, not medical or legal determinations.
    # They only prioritize a human queue; they never publish or reject a report.
    normalized_text = complaint_text.casefold()
    explicit_hazard = any(term in normalized_text for term in HIGH_RISK_TERMS)
    if category == "Adulteration" or confidence < 0.45 or explicit_hazard:
        return "High — human review requested"
    return "Standard — human review required"



@st.cache_data(ttl=OSM_CACHE_SECONDS, show_spinner=False)
def fetch_hyderabad_restaurants() -> dict:
    """Fetch and cache parsed OSM data; keep network and parsing logic testable."""
    return fetch_osm_restaurants()


def render_map(view: str, venues: pd.DataFrame, reports: list[dict]) -> None:
    """Render live OSM venue locations and explicitly human-approved complaint markers."""
    if venues.empty:
        st.warning("No named OSM restaurants are available. The app does not substitute sample venues.")
        return
    center = {"lat": float(venues["lat"].mean()), "lon": float(venues["lon"].mean())}
    approved = [item for item in reports if item["status"] == "Approved"]

    if view == "Citizen View — Approved report locations":
        fig = px.scatter_mapbox(
            venues, lat="lat", lon="lon", hover_name="name", color="cuisine",
            hover_data={"area": True, "address": True, "osm_ref": True, "lat": False, "lon": False},
            zoom=10, center=center, mapbox_style="carto-positron",
            title="OpenStreetMap restaurant locations and approved reports",
        )
        geolocated = [
            item for item in approved
            if item.get("venue_lat") is not None and item.get("venue_lon") is not None
        ]
        if geolocated:
            report_frame = pd.DataFrame(geolocated)
            fig.add_trace(
                go.Scattermapbox(
                    lat=report_frame["venue_lat"], lon=report_frame["venue_lon"],
                    mode="markers", name="Human-approved reports",
                    marker={"size": 15, "color": "#dc2626"},
                    text=report_frame["venue"],
                    customdata=report_frame[["category", "area"]].to_numpy(),
                    hovertemplate=(
                        "<b>Approved report · %{text}</b>"
                        "<br>Category: %{customdata[0]}"
                        "<br>Area: %{customdata[1]}<extra></extra>"
                    ),
                )
            )
        st.plotly_chart(fig, use_container_width=True)
        st.metric("Human-approved complaints", len(approved))
        without_location = len(approved) - len(geolocated)
        if without_location:
            st.caption(
                f"{without_location} approved complaint(s) have no selected OSM venue "
                "and are not assigned invented map coordinates."
            )
        if not approved:
            st.info("No complaints have been approved yet. Pending complaints are never shown.")
    else:
        supply = (
            venues.groupby("area", dropna=False)
            .agg(listed_restaurants=("osm_ref", "count"), lat=("lat", "mean"), lon=("lon", "mean"))
            .reset_index()
            .sort_values("listed_restaurants", ascending=True)
        )
        fig = px.scatter_mapbox(
            supply, lat="lat", lon="lon", size="listed_restaurants",
            color="listed_restaurants", hover_name="area",
            hover_data={"listed_restaurants": True, "lat": False, "lon": False},
            color_continuous_scale="Teal", size_max=34, zoom=10, center=center,
            mapbox_style="carto-positron",
            title="Restaurant supply represented in OpenStreetMap",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(
            supply[["area", "listed_restaurants"]].rename(
                columns={"area": "OSM-tagged area", "listed_restaurants": "Named restaurants"}
            ),
            use_container_width=True, hide_index=True,
        )
        st.warning(
            "Population-density data is not connected. This is an OSM restaurant "
            "supply view, not a validated population-versus-supply market-gap analysis."
        )

    st.markdown(
        '[Map data: OpenStreetMap contributors](https://www.openstreetmap.org/copyright) '
        '· Open Database License (ODbL)'
    )




initialize_session_state()

st.markdown(
    """
    <style>
      .stApp { background: radial-gradient(circle at 12% 0%, #18334a 0, #0b1422 36%, #08111d 100%); }
      .main .block-container { max-width: 1380px; padding-top: 2.1rem; padding-bottom: 3rem; }
      [data-testid="stHeader"] { background: rgba(8, 17, 29, 0.72); }
      [data-testid="stMetric"] { background: #122338; border: 1px solid #27445b; padding: 1rem; border-radius: 14px; }
      [data-testid="stMetricValue"] { color: #eff6ff; }
      [data-testid="stMetricLabel"] { color: #a9c0d2; }
      .stTabs [data-baseweb="tab-list"] { gap: .35rem; border-bottom: 1px solid #294256; }
      .stTabs [data-baseweb="tab"] { background: #122338; border-radius: 10px 10px 0 0; padding: .65rem 1rem; }
      .stTabs [aria-selected="true"] { background: #164e63; color: #ecfeff; }
      div.stButton > button, div.stLinkButton > a, div.stFormSubmitButton > button {
        border-radius: 10px; border: 1px solid #2b6576; font-weight: 650;
      }
      [data-testid="stExpander"] { border: 1px solid #294256; border-radius: 12px; }
      [data-testid="stAlert"] { border-radius: 12px; }
      .cs-hero { background: linear-gradient(115deg, #112d42, #123c4a 62%, #173b55);
        border: 1px solid #2b6474; border-radius: 20px; padding: 1.35rem 1.5rem; margin: .5rem 0 1.1rem; }
      .cs-eyebrow { color: #7dd3c7; font-size: .78rem; letter-spacing: .14em; text-transform: uppercase; font-weight: 700; }
      .cs-title { color: #f1f7fb; font-size: 2.15rem; font-weight: 800; line-height: 1.12; margin: .35rem 0; }
      .cs-subtitle { color: #c3d6e2; font-size: 1rem; margin: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="cs-hero">
      <div class="cs-eyebrow">Civic intelligence · Hyderabad</div>
      <div class="cs-title">Food safety, made more transparent.</div>
      <p class="cs-subtitle">Open data for discovery. Human judgment for moderation. Clear provenance at every step.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Data connection")
    st.caption("OpenStreetMap · Overpass API")
    if st.button("Refresh restaurant snapshot", use_container_width=True):
        fetch_hyderabad_restaurants.clear()
        st.rerun()
    st.caption("Automatic cache: 6 hours. Manual refresh is available above.")

osm_snapshot = None
osm_error = None
with st.spinner("Loading Hyderabad restaurant records from OpenStreetMap…"):
    try:
        osm_snapshot = fetch_hyderabad_restaurants()
    except RuntimeError as exc:
        osm_error = str(exc)
    except Exception:
        osm_error = "Unexpected data-source error. Live restaurant records are unavailable."

if osm_snapshot is not None:
    OSM_VENUES = pd.DataFrame(osm_snapshot["records"])
    if OSM_VENUES.empty:
        st.warning("Overpass responded successfully, but no named restaurants matched this query.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Named restaurants", f"{len(OSM_VENUES):,}")
        m2.metric("OSM-tagged areas", OSM_VENUES["area"].nunique())
        m3.metric("Data source", "Overpass API")
    st.caption(
        f"OSM data timestamp: {osm_snapshot['osm_data_timestamp']} · "
        f"Fetched (UTC): {osm_snapshot['fetched_at_utc']}"
    )
else:
    OSM_VENUES = pd.DataFrame(
        columns=["osm_ref", "osm_url", "name", "cuisine", "area", "address", "lat", "lon", "amenity", "source"]
    )
    st.error(f"Live OpenStreetMap data is unavailable: {osm_error}")
    st.info("No sample restaurant fallback is loaded. Retry later or check your connection.")

st.title("🛡️ CivicShield V2")
st.subheader("Food safety, made more transparent.")
st.write(
    "An evidence-led civic technology prototype connecting citizen observations, "
    "human review, public visibility and restaurant response workflows."
)

with st.container(border=True):
    st.markdown("**Evidence before claims. Human review before publication.**")
    st.caption(
        "Live venue discovery uses OpenStreetMap records. OSM listings do not certify "
        "a restaurant's food safety or FSSAI licence status."
    )
    st.link_button("Open official FoSCoS verification portal", FOOD_SAFETY_PORTAL)

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

    area_options = (
        sorted(OSM_VENUES["area"].dropna().unique().tolist())
        if not OSM_VENUES.empty
        else ["Area not available"]
    )
    venue_lookup = {}
    if not OSM_VENUES.empty:
        for venue_record in OSM_VENUES.to_dict(orient="records"):
            # OSM can contain multiple businesses with the same name.
            # Include the stable OSM reference in the visible option to disambiguate.
            venue_label = (
                f"{venue_record['name']} — {venue_record['area']} "
                f"[{venue_record['osm_ref']}]"
            )
            venue_lookup[venue_label] = venue_record
    with st.form("citizen_complaint_form", clear_on_submit=True):
        selected_area = st.selectbox("Area", area_options)
        selected_venue = st.selectbox(
            "Venue (optional)",
            ["Not specified"] + list(venue_lookup),
            help="Only venues returned by the current OpenStreetMap snapshot appear here. Duplicate names are disambiguated by area and OSM ID.",
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
                "venue": venue_lookup.get(selected_venue, {}).get("name"),
                "venue_lat": venue_lookup.get(selected_venue, {}).get("lat"),
                "venue_lon": venue_lookup.get(selected_venue, {}).get("lon"),
                "osm_ref": venue_lookup.get(selected_venue, {}).get("osm_ref"),
                "text": cleaned_text,
                "category": category,
                "confidence": confidence,
                "priority": priority_for(category, confidence, cleaned_text),
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
            "Citizen View — Approved report locations",
            "Brand View — Restaurant supply coverage",
        ],
        horizontal=True,
    )
    render_map(selected_view, OSM_VENUES, st.session_state.complaints)

    with st.expander("Explore live OpenStreetMap restaurant records"):
        if OSM_VENUES.empty:
            st.info("No live records are available in this session.")
        else:
            st.dataframe(
                OSM_VENUES[["name", "cuisine", "area", "address", "osm_ref", "osm_url"]],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "osm_url": st.column_config.LinkColumn("OpenStreetMap record"),
                    "osm_ref": "OSM object ID",
                },
            )
            st.caption(
                f"{len(OSM_VENUES):,} named restaurant objects in the cached Overpass response. "
                "Only mapped and named OSM objects are represented."
            )

    st.subheader("Restaurant directory")
    venue_search = st.text_input(
        "Search by restaurant, cuisine or OSM-tagged area",
        placeholder="Try a restaurant name, cuisine or neighbourhood",
        key="osm_venue_search",
    )
    filtered_venues = OSM_VENUES.copy()
    if venue_search.strip():
        searchable = (
            filtered_venues[["name", "cuisine", "area", "address"]]
            .fillna("")
            .astype(str)
            .agg(" ".join, axis=1)
        )
        filtered_venues = filtered_venues[
            searchable.str.contains(venue_search.strip(), case=False, regex=False)
        ]
    st.caption(f"{len(filtered_venues):,} matching named OSM restaurant records")
    if filtered_venues.empty:
        st.info("No matching OSM restaurant records in the current cached snapshot.")
    else:
        card_limit = min(len(filtered_venues), 12)
        for offset in range(0, card_limit, 3):
            card_columns = st.columns(3)
            for card_column, venue in zip(
                card_columns,
                filtered_venues.iloc[offset : offset + 3].to_dict(orient="records"),
            ):
                with card_column:
                    with st.container(border=True):
                        st.text(venue["name"])
                        st.caption(f"{venue['cuisine']} · {venue['area']}")
                        st.write(venue["address"])
                        st.link_button(
                            "View OSM record",
                            venue["osm_url"],
                            use_container_width=True,
                        )
        if len(filtered_venues) > card_limit:
            st.caption(f"Showing the first {card_limit} results. Refine the search to narrow the list.")

    with st.expander("Data coverage and market-gap limitations"):
        st.write(
            "The live layer measures restaurant listings recorded in OSM. It does not "
            "provide population density, footfall, spending power or official business "
            "completeness. A true market-gap model requires a separately sourced and "
            "licensed demographic layer."
        )
        st.markdown(
            "[OpenStreetMap data and ODbL attribution](https://www.openstreetmap.org/copyright) "
            "· [Overpass API documentation](https://wiki.openstreetmap.org/wiki/Overpass_API)"
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
        - **Venue data:** named restaurant objects fetched from OpenStreetMap through Overpass; cached for six hours.
        - **Coverage:** only named restaurant objects with valid coordinates inside the query bounding box are shown; OSM completeness is not guaranteed.
        - **Area labels:** derived from OSM address tags and may be missing or broad.
        - **Map data licence:** OpenStreetMap contributors, ODbL; [copyright and attribution details]({OSM_COPYRIGHT_URL}).
        - **Demographics:** no population-density dataset is integrated; Brand View shows OSM restaurant supply only.
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
