from __future__ import annotations

import requests
import pytest

from v2.osm_data import (
    HYDERABAD_BBOX,
    build_overpass_query,
    fetch_osm_restaurants,
    parse_overpass_payload,
)


def test_query_contains_bbox_and_all_osm_object_types():
    query = build_overpass_query()
    assert 'node["amenity"="restaurant"]' in query
    assert 'way["amenity"="restaurant"]' in query
    assert 'relation["amenity"="restaurant"]' in query
    for coordinate in ("17.2", "78.3", "17.55", "78.62"):
        assert coordinate in query


def test_parser_normalizes_node_way_and_relation_and_uses_way_centres():
    payload = {
        "elements": [
            {
                "type": "node", "id": 101, "lat": 17.44, "lon": 78.38,
                "tags": {"amenity": "restaurant", "name": "Node Kitchen", "cuisine": "south_indian",
                         "addr:suburb": "Madhapur", "addr:street": "Sample Road"},
            },
            {
                "type": "way", "id": 202, "center": {"lat": 17.45, "lon": 78.39},
                "tags": {"amenity": "restaurant", "name": "Way Cafe"},
            },
            {
                "type": "relation", "id": 303, "center": {"lat": 17.43, "lon": 78.40},
                "tags": {"amenity": "restaurant", "name": "Relation Diner"},
            },
        ],
        "osm3s": {"timestamp_osm_base": "2026-11-12T00:00:00Z"},
    }
    records = parse_overpass_payload(payload)
    assert {record["osm_ref"] for record in records} == {"node/101", "way/202", "relation/303"}
    node = next(record for record in records if record["osm_ref"] == "node/101")
    assert node["name"] == "Node Kitchen"
    assert node["cuisine"] == "South Indian"
    assert node["area"] == "Madhapur"
    assert node["lat"] == pytest.approx(17.44)
    assert node["lon"] == pytest.approx(78.38)
    assert node["osm_url"].endswith("/node/101")


def test_parser_keeps_duplicate_business_names_with_distinct_osm_ids():
    payload = {
        "elements": [
            {"type": "node", "id": 11, "lat": 17.44, "lon": 78.38,
             "tags": {"amenity": "restaurant", "name": "Same Brand", "addr:suburb": "Madhapur"}},
            {"type": "node", "id": 12, "lat": 17.45, "lon": 78.39,
             "tags": {"amenity": "restaurant", "name": "Same Brand", "addr:suburb": "Gachibowli"}},
        ]
    }
    records = parse_overpass_payload(payload)
    assert len(records) == 2
    assert {record["osm_ref"] for record in records} == {"node/11", "node/12"}


def test_parser_filters_unnamed_wrong_type_missing_coordinates_and_outside_bbox():
    payload = {
        "elements": [
            {"type": "node", "id": 1, "lat": 17.4, "lon": 78.4, "tags": {"amenity": "restaurant"}},
            {"type": "node", "id": 2, "lat": 17.4, "lon": 78.4, "tags": {"amenity": "cafe", "name": "Cafe"}},
            {"type": "node", "id": 3, "tags": {"amenity": "restaurant", "name": "No Coordinates"}},
            {"type": "node", "id": 4, "lat": 19.0, "lon": 78.4, "tags": {"amenity": "restaurant", "name": "Outside"}},
            {"type": "node", "id": 5, "lat": "invalid", "lon": 78.4, "tags": {"amenity": "restaurant", "name": "Bad Coordinates"}},
        ]
    }
    assert parse_overpass_payload(payload) == []


def test_parser_rejects_malformed_payload():
    with pytest.raises(ValueError, match="elements list"):
        parse_overpass_payload({"elements": None})


def test_fetch_posts_query_with_user_agent_and_returns_provenance(monkeypatch):
    payload = {
        "elements": [
            {"type": "node", "id": 707, "lat": 17.44, "lon": 78.38,
             "tags": {"amenity": "restaurant", "name": "Test Restaurant"}}
        ],
        "osm3s": {"timestamp_osm_base": "2026-11-12T00:00:00Z"},
    }

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return payload

    captured = {}

    def fake_post(url, data, headers, timeout):
        captured.update({"url": url, "data": data, "headers": headers, "timeout": timeout})
        return FakeResponse()

    monkeypatch.setattr("v2.osm_data.requests.post", fake_post)
    result = fetch_osm_restaurants()
    assert result["record_count"] == 1
    assert result["records"][0]["osm_ref"] == "node/707"
    assert result["osm_data_timestamp"] == "2026-11-12T00:00:00Z"
    assert result["query_bbox"] == list(HYDERABAD_BBOX)
    assert "overpass-api.de/api/interpreter" in captured["url"]
    assert 'amenity"="restaurant' in captured["data"]["data"]
    assert "CivicShield/2.1" in captured["headers"]["User-Agent"]


def test_fetch_maps_rate_limit_to_actionable_error(monkeypatch):
    class FakeResponse:
        status_code = 429

    def fake_post(*args, **kwargs):
        raise requests.HTTPError("429 rate limited", response=FakeResponse())

    monkeypatch.setattr("v2.osm_data.requests.post", fake_post)
    with pytest.raises(RuntimeError, match="temporarily busy"):
        fetch_osm_restaurants()
