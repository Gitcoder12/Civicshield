from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_streamlit_app_submit_approve_and_reject_flow(monkeypatch):
    """Exercise V2's UI using a deterministic Overpass response, without live network."""
    payload = {
        "elements": [
            {
                "type": "node",
                "id": 501,
                "lat": 17.4483,
                "lon": 78.3915,
                "tags": {
                    "amenity": "restaurant",
                    "name": "QA Test Kitchen",
                    "cuisine": "indian",
                    "addr:suburb": "Madhapur",
                    "addr:street": "Test Road",
                },
            },
            {
                "type": "node",
                "id": 502,
                "lat": 17.4401,
                "lon": 78.3489,
                "tags": {
                    "amenity": "restaurant",
                    "name": "QA Test Kitchen",
                    "cuisine": "indian",
                    "addr:suburb": "Gachibowli",
                    "addr:street": "Demo Avenue",
                },
            },
        ],
        "osm3s": {"timestamp_osm_base": "2026-11-12T00:00:00Z"},
    }

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    monkeypatch.setattr("v2.osm_data.requests.post", lambda *args, **kwargs: FakeResponse())

    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "v2" / "app_v2.py", default_timeout=60).run()
    assert not app.exception
    assert any("CivicShield V2" in item.value for item in app.title)

    venue_selector = next(item for item in app.selectbox if item.label == "Venue (optional)")
    assert len(venue_selector.options) == 3
    assert venue_selector.options[1] != venue_selector.options[2]

    area_selector = next(item for item in app.selectbox if item.label == "Area")
    area_selector.select("Madhapur")
    madhapur_option = next(option for option in venue_selector.options if "[node/501]" in option)
    venue_selector.select(madhapur_option)
    app.text_area[0].set_value("I found a hair in my food")

    submit_button = next(item for item in app.button if item.label == "Submit for human review")
    submit_button.click().run()

    reports = app.session_state["complaints"]
    assert len(reports) == 1
    assert reports[0]["status"] == "Pending"
    assert reports[0]["category"] == "Hygiene"
    assert reports[0]["osm_ref"] == "node/501"
    assert reports[0]["venue"] == "QA Test Kitchen"
    assert reports[0]["area"] == "Madhapur"

    assert not app.exception

    approve_button = next(item for item in app.button if item.label == "Approve for public map")
    approve_button.click().run()
    assert app.session_state["complaints"][0]["status"] == "Approved"
    assert not app.exception

    # Deliberately choose a UI area that conflicts with the selected venue's OSM tag.
    # The saved report must use the OSM venue's tagged area for correct map placement.
    area_selector = next(item for item in app.selectbox if item.label == "Area")
    venue_selector = next(item for item in app.selectbox if item.label == "Venue (optional)")
    area_selector.select("Madhapur")
    gachibowli_option = next(option for option in venue_selector.options if "[node/502]" in option)
    venue_selector.select(gachibowli_option)
    app.text_area[0].set_value("The waiter looked at me funny")
    submit_button = next(item for item in app.button if item.label == "Submit for human review")
    submit_button.click().run()
    assert len(app.session_state["complaints"]) == 2
    assert app.session_state["complaints"][1]["status"] == "Pending"
    assert app.session_state["complaints"][1]["area"] == "Gachibowli"
    assert app.session_state["complaints"][1]["osm_ref"] == "node/502"

    reject_button = next(item for item in app.button if item.label == "Reject")
    reject_button.click().run()
    assert app.session_state["complaints"][1]["status"] == "Rejected"
    assert app.session_state["complaints"][0]["status"] == "Approved"
    assert not app.exception
