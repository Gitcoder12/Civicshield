"""OpenStreetMap/Overpass data access for CivicShield V2.

This module has no Streamlit dependency so parsing and HTTP behaviour can be
unit-tested independently of the interactive application.
"""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HYDERABAD_BBOX = (17.20, 78.30, 17.55, 78.62)  # south, west, north, east
OSM_CACHE_SECONDS = 6 * 60 * 60
OSM_USER_AGENT = "CivicShield/2.1 (https://github.com/Gitcoder12/Civicshield)"


def build_overpass_query(
    bbox: tuple[float, float, float, float] = HYDERABAD_BBOX,
) -> str:
    """Build a bounded query for restaurant nodes, ways and relations."""
    south, west, north, east = bbox
    return f"""
    [out:json][timeout:50];
    (
      node["amenity"="restaurant"]({south},{west},{north},{east});
      way["amenity"="restaurant"]({south},{west},{north},{east});
      relation["amenity"="restaurant"]({south},{west},{north},{east});
    );
    out center tags;
    """


def parse_overpass_payload(
    payload: dict[str, Any],
    bbox: tuple[float, float, float, float] = HYDERABAD_BBOX,
) -> list[dict[str, Any]]:
    """Normalize named restaurant objects and discard malformed/out-of-area rows."""
    if not isinstance(payload, dict) or not isinstance(payload.get("elements"), list):
        raise TypeError("Overpass response must be an object containing an elements list.")

    south, west, north, east = bbox
    records: list[dict[str, Any]] = []
    seen_refs: set[str] = set()

    for element in payload["elements"]:
        if not isinstance(element, dict):
            continue
        tags = element.get("tags") or {}
        if not isinstance(tags, dict) or tags.get("amenity") != "restaurant":
            continue

        name = str(tags.get("name") or "").strip()
        if not name:
            continue

        center = element.get("center") or {}
        lat = element.get("lat", center.get("lat"))
        lon = element.get("lon", center.get("lon"))
        if lat is None or lon is None:
            continue
        try:
            lat, lon = float(lat), float(lon)
        except (TypeError, ValueError):
            continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            continue
        if not (south <= lat <= north and west <= lon <= east):
            continue

        osm_type = str(element.get("type") or "")
        osm_id = str(element.get("id") or "")
        if osm_type not in {"node", "way", "relation"} or not osm_id.isdigit():
            continue
        osm_ref = f"{osm_type}/{osm_id}"
        if osm_ref in seen_refs:
            continue
        seen_refs.add(osm_ref)

        area = (
            tags.get("addr:suburb")
            or tags.get("addr:neighbourhood")
            or tags.get("addr:city_district")
            or tags.get("addr:district")
            or tags.get("addr:city")
            or tags.get("addr:place")
            or "Area not tagged in OSM"
        )
        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb") or tags.get("addr:neighbourhood"),
            tags.get("addr:city"),
        ]
        address = ", ".join(str(part) for part in address_parts if part) or "Address not tagged in OSM"

        records.append(
            {
                "osm_ref": osm_ref,
                "osm_url": f"https://www.openstreetmap.org/{osm_ref}",
                "name": name,
                "cuisine": str(tags.get("cuisine", "Not tagged")).replace("_", " ").title(),
                "area": str(area),
                "address": address,
                "lat": lat,
                "lon": lon,
                "amenity": "restaurant",
                "source": "OpenStreetMap via Overpass API",
            }
        )

    records.sort(key=lambda item: (item["area"].casefold(), item["name"].casefold(), item["osm_ref"]))
    return records



def build_venue_option_lookup(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Create unique, human-readable selectbox labels for OSM records.

    Business names are not unique: restaurant chains commonly reuse names.
    OSM object references make each option deterministic and unambiguous.
    """
    lookup: dict[str, dict[str, Any]] = {}
    for record in records:
        name = str(record.get("name") or "").strip()
        area = str(record.get("area") or "Area not tagged in OSM")
        osm_ref = str(record.get("osm_ref") or "").strip()
        if not name or not osm_ref:
            continue
        label = f"{name} — {area} [{osm_ref}]"
        lookup[label] = record
    return lookup


def fetch_osm_restaurants(
    timeout: tuple[int, int] = (10, 70),
    bbox: tuple[float, float, float, float] = HYDERABAD_BBOX,
) -> dict[str, Any]:
    """Fetch and normalize one Overpass snapshot; raise clear errors on failure."""
    query = build_overpass_query(bbox)
    headers = {
        "User-Agent": OSM_USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": query},
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout as exc:
        raise RuntimeError("Overpass timed out. Please retry after a short interval.") from exc
    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        if status in (429, 502, 503, 504):
            message = f"Overpass is temporarily busy (HTTP {status}). Please retry later."
        else:
            message = f"Overpass returned HTTP {status}. Live venue data is unavailable."
        raise RuntimeError(message) from exc
    except requests.RequestException as exc:
        raise RuntimeError("Could not reach Overpass. Check your internet connection and retry.") from exc
    except ValueError as exc:
        raise RuntimeError("Overpass returned invalid JSON. Live venue data is unavailable.") from exc

    records = parse_overpass_payload(payload, bbox=bbox)
    osm_meta = payload.get("osm3s") or {}
    return {
        "records": records,
        "osm_data_timestamp": osm_meta.get("timestamp_osm_base", "Not supplied by Overpass"),
        "fetched_at_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "record_count": len(records),
        "query_bbox": list(bbox),
    }
