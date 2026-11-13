from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import backend_app


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    hotels_file = tmp_path / "hotels.json"
    reports_file = tmp_path / "reports.json"
    hotels_file.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "name": "Demo Venue 001",
                    "base_score": 80,
                    "adulteration_flag": False,
                },
                {
                    "id": 2,
                    "name": "Demo Venue 002",
                    "base_score": 55,
                    "adulteration_flag": False,
                },
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(backend_app, "HOTELS_FILE", hotels_file)
    monkeypatch.setattr(backend_app, "REPORTS_FILE", reports_file)
    app = backend_app.create_app({"TESTING": True})
    return app.test_client(), hotels_file, reports_file


def test_health_and_security_headers(client: Any) -> None:
    test_client, _, _ = client
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok", "mode": "local-demo"}
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_venue_lookup_does_not_mutate_source_records(client: Any) -> None:
    test_client, hotels_file, _ = client
    before = hotels_file.read_text(encoding="utf-8")
    response = test_client.get("/hotel/2")
    after = hotels_file.read_text(encoding="utf-8")

    assert response.status_code == 200
    assert [item["id"] for item in response.json["better_nearby"]] == [1]
    assert before == after


def test_unknown_venue_returns_404(client: Any) -> None:
    test_client, _, _ = client
    assert test_client.get("/hotel/999").status_code == 404


def test_report_requires_json_object(client: Any) -> None:
    test_client, _, _ = client
    assert test_client.post("/submit_report", data="not json").status_code == 415
    response = test_client.post("/submit_report", json=["not", "an", "object"])
    assert response.status_code == 400


@pytest.mark.parametrize(
    ("payload", "status"),
    [
        ({"hotel_id": "1"}, 400),
        ({"hotel_id": True}, 400),
        ({"hotel_id": 999}, 404),
        ({"hotel_id": 1, "mode": "inspector"}, 403),
        ({"hotel_id": 1, "checklist": []}, 400),
        ({"hotel_id": 1, "checklist": {"pests_seen": "yes"}}, 400),
        ({"hotel_id": 1, "checklist": {"made_up": True}}, 400),
        ({"hotel_id": 1, "notes": "x" * 1001}, 400),
        ({"hotel_id": 1, "notes": 42}, 400),
    ],
)
def test_invalid_reports_are_rejected(client: Any, payload: dict[str, Any], status: int) -> None:
    test_client, _, reports_file = client
    response = test_client.post("/submit_report", json=payload)
    assert response.status_code == status
    assert not reports_file.exists()


def test_customer_report_is_unverified_and_never_changes_official_score(client: Any) -> None:
    test_client, hotels_file, reports_file = client
    before = json.loads(hotels_file.read_text(encoding="utf-8"))
    response = test_client.post(
        "/submit_report",
        json={
            "hotel_id": 1,
            "mode": "customer",
            "checklist": {
                "clean_dining_area": False,
                "pests_seen": True,
                "food_adulteration": True,
            },
            "notes": "<script>alert(1)</script>",
        },
    )

    assert response.status_code == 201
    assert response.json["success"] is True
    assert response.json["verified"] is False
    assert response.json["official_score_changed"] is False
    after = json.loads(hotels_file.read_text(encoding="utf-8"))
    assert after == before

    saved = json.loads(reports_file.read_text(encoding="utf-8"))
    assert len(saved) == 1
    assert saved[0]["verified"] is False
    assert saved[0]["official_score_at_submission"] == 80
    assert saved[0]["notes"] == "<script>alert(1)</script>"
    fetched = test_client.get(f"/report/{response.json['report_id']}")
    assert fetched.status_code == 200
    assert fetched.json["verified"] is False


def test_report_storage_uses_atomic_replace(client: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    test_client, _, reports_file = client
    response = test_client.post(
        "/submit_report",
        json={"hotel_id": 1, "mode": "customer", "checklist": {}, "notes": "hello"},
    )
    assert response.status_code == 201
    assert reports_file.exists()
    assert not list(reports_file.parent.glob(".reports.json.*.tmp"))


def test_calculate_score_is_bounded_and_validates_base_score() -> None:
    assert backend_app.calculate_score(
        80, {"clean_dining_area": False, "pests_seen": True}
    ) == 57
    assert backend_app.calculate_score(5, {"food_adulteration": True}) == 0
    with pytest.raises(ValueError):
        backend_app.calculate_score(101, {})


def test_cors_allows_local_demo_origin_but_not_arbitrary_origins(client: Any) -> None:
    test_client, _, _ = client
    allowed = test_client.get(
        "/health", headers={"Origin": "http://localhost:5000"}
    )
    rejected = test_client.get(
        "/health", headers={"Origin": "https://attacker.example"}
    )

    assert (
        allowed.headers.get("Access-Control-Allow-Origin") == "http://localhost:5000"
    )
    assert "Access-Control-Allow-Origin" not in rejected.headers
