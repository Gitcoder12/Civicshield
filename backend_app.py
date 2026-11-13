"""Local demo API for CivicShield.

This service stores community reports as unverified observations. It never changes
venue inspection scores or official-looking license fields based on citizen input.
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
HOTELS_FILE = BASE_DIR / "hotels.json"
REPORTS_FILE = BASE_DIR / "reports.json"
_STORAGE_LOCK = threading.RLock()

CHECKLIST_DEDUCTIONS = {
    "clean_dining_area": 8,
    "staff_hygiene": 10,
    "food_freshness": 12,
    "bad_smell": 8,
    "pests_seen": 15,
    "dirty_utensils": 10,
    "food_adulteration": 20,
    "food_storage_safe": 10,
    "temperature_control": 10,
    "cross_contamination": 12,
    "ingredient_quality": 10,
    "kitchen_sanitation": 10,
    "waste_disposal": 8,
    "water_quality": 10,
    "pest_control_fail": 12,
}
NEGATIVE_CHECKS = {
    "clean_dining_area",
    "staff_hygiene",
    "food_freshness",
    "food_storage_safe",
    "temperature_control",
    "ingredient_quality",
    "kitchen_sanitation",
    "waste_disposal",
    "water_quality",
}
POSITIVE_CHECKS = set(CHECKLIST_DEDUCTIONS) - NEGATIVE_CHECKS


def _read_json(path: Path, default: Any) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def load_hotels() -> list[dict[str, Any]]:
    data = _read_json(HOTELS_FILE, [])
    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        raise ValueError("venue dataset must be a JSON array of objects")
    return data


def load_reports() -> list[dict[str, Any]]:
    data = _read_json(REPORTS_FILE, [])
    if not isinstance(data, list) or any(not isinstance(item, dict) for item in data):
        raise ValueError("reports file must be a JSON array of objects")
    return data


def save_reports(data: list[dict[str, Any]]) -> None:
    _atomic_write_json(REPORTS_FILE, data)


def calculate_score(base_score: int, checklist: dict[str, bool]) -> int:
    """Return an illustrative community signal; never treat it as an official score."""
    if isinstance(base_score, bool) or not isinstance(base_score, int) or not 0 <= base_score <= 100:
        raise ValueError("base_score must be an integer from 0 to 100")
    deductions = 0
    for key, value in checklist.items():
        if key in NEGATIVE_CHECKS and not value:
            deductions += CHECKLIST_DEDUCTIONS[key]
        elif key in POSITIVE_CHECKS and value:
            deductions += CHECKLIST_DEDUCTIONS[key]
    return max(0, min(100, base_score - deductions))


def _validate_checklist(value: Any) -> dict[str, bool]:
    if not isinstance(value, dict):
        raise ValueError("checklist must be an object")
    unknown = set(value) - set(CHECKLIST_DEDUCTIONS)
    if unknown:
        raise ValueError(f"unknown checklist fields: {', '.join(sorted(unknown))}")
    if any(type(flag) is not bool for flag in value.values()):
        raise ValueError("checklist values must be booleans")
    return value


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=16 * 1024)
    if test_config:
        app.config.update(test_config)

    allowed_origins = os.getenv(
        "CIVICSHIELD_CORS_ORIGINS",
        "http://localhost:5000,http://127.0.0.1:5000",
    )
    origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
    CORS(app, origins=origins)

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    @app.get("/")
    def index():
        return send_from_directory(BASE_DIR, "index.html")

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "mode": "local-demo"})

    @app.get("/hotels")
    def get_hotels():
        try:
            return jsonify(load_hotels())
        except (OSError, ValueError, json.JSONDecodeError):
            app.logger.exception("Unable to load venue demo data")
            return jsonify({"error": "Venue data is unavailable"}), 500

    @app.get("/hotel/<int:hotel_id>")
    def get_hotel(hotel_id: int):
        try:
            hotels = load_hotels()
        except (OSError, ValueError, json.JSONDecodeError):
            app.logger.exception("Unable to load venue demo data")
            return jsonify({"error": "Venue data is unavailable"}), 500

        hotel = next((item for item in hotels if item.get("id") == hotel_id), None)
        if hotel is None:
            return jsonify({"error": "Venue not found"}), 404

        result = dict(hotel)
        if result.get("base_score", 100) < 60:
            result["better_nearby"] = sorted(
                (
                    item
                    for item in hotels
                    if item.get("base_score", 0) > result["base_score"]
                    and item.get("id") != hotel_id
                ),
                key=lambda item: item.get("base_score", 0),
                reverse=True,
            )[:3]
        else:
            result["better_nearby"] = []
        return jsonify(result)

    @app.post("/submit_report")
    def submit_report():
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400

        hotel_id = data.get("hotel_id")
        if isinstance(hotel_id, bool) or not isinstance(hotel_id, int):
            return jsonify({"error": "hotel_id must be an integer"}), 400

        mode = data.get("mode", "customer")
        if mode != "customer":
            return jsonify({"error": "Inspector submissions require an authenticated authority account"}), 403

        try:
            checklist = _validate_checklist(data.get("checklist", {}))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        notes = data.get("notes", "")
        if not isinstance(notes, str):
            return jsonify({"error": "notes must be text"}), 400
        notes = notes.strip()
        if len(notes) > 1000:
            return jsonify({"error": "notes must be 1000 characters or fewer"}), 400

        try:
            hotels = load_hotels()
        except (OSError, ValueError, json.JSONDecodeError):
            app.logger.exception("Unable to load venue demo data")
            return jsonify({"error": "Venue data is unavailable"}), 500

        hotel = next((item for item in hotels if item.get("id") == hotel_id), None)
        if hotel is None:
            return jsonify({"error": "Venue not found"}), 404

        base_score = hotel.get("base_score", 0)
        if isinstance(base_score, bool) or not isinstance(base_score, int):
            return jsonify({"error": "Venue score data is invalid"}), 500

        suggested_score = calculate_score(base_score, checklist)
        adulteration_reported = bool(checklist.get("food_adulteration", False))
        refund_triggers = [
            label
            for key, label in (
                ("food_adulteration", "suspected food adulteration"),
                ("bad_smell", "bad smell reported"),
                ("foreign_object", "foreign object in food"),
                ("food_poisoning", "food poisoning reported"),
            )
            if checklist.get(key, False)
        ]

        report = {
            "report_id": f"CS-{uuid.uuid4().hex[:8].upper()}",
            "hotel_id": hotel_id,
            "hotel_name": str(hotel.get("name", "Unknown venue")),
            "mode": "customer",
            "checklist": checklist,
            "suggested_community_signal": suggested_score,
            "official_score_at_submission": base_score,
            "official_score_changed": False,
            "notes": notes,
            "adulteration_reported": adulteration_reported,
            "refund_triggers": refund_triggers,
            "verified": False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            with _STORAGE_LOCK:
                reports = load_reports()
                reports.append(report)
                save_reports(reports)
        except (OSError, ValueError, json.JSONDecodeError):
            app.logger.exception("Unable to save community report")
            return jsonify({"error": "Report could not be saved"}), 500

        return jsonify(
            {
                "success": True,
                "report_id": report["report_id"],
                "suggested_community_signal": suggested_score,
                "official_score_changed": False,
                "verified": False,
                "refund_triggers": refund_triggers,
            }
        ), 201

    @app.get("/report/<report_id>")
    def get_report(report_id: str):
        try:
            reports = load_reports()
        except (OSError, ValueError, json.JSONDecodeError):
            app.logger.exception("Unable to load community reports")
            return jsonify({"error": "Reports are unavailable"}), 500

        report = next((item for item in reports if item.get("report_id") == report_id), None)
        if report is None:
            return jsonify({"error": "Report not found"}), 404
        return jsonify(report)

    return app


app = create_app()


if __name__ == "__main__":
    print("\nCivicShield local demo is running at http://127.0.0.1:5000\n")
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=os.getenv("FLASK_DEBUG", "0") == "1",
    )
