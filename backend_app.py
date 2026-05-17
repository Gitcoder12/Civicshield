import json
import os
import uuid
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

BASE_DIR = os.path.dirname(__file__)
HOTELS_FILE = os.path.join(BASE_DIR, "hotels.json")
REPORTS_FILE = os.path.join(BASE_DIR, "reports.json")


def load_hotels():
    with open(HOTELS_FILE, "r") as f:
        return json.load(f)


def save_hotels(data):
    with open(HOTELS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_reports():
    if not os.path.exists(REPORTS_FILE):
        return []
    with open(REPORTS_FILE, "r") as f:
        return json.load(f)


def save_reports(data):
    with open(REPORTS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def calculate_score(base_score, checklist):
    """
    Recalculate hygiene score from checklist.
    Each failed item deducts points from base_score.
    """
    deductions = 0

    # Customer report deductions
    if not checklist.get("clean_dining_area", True):
        deductions += 8
    if not checklist.get("staff_hygiene", True):
        deductions += 10
    if not checklist.get("food_freshness", True):
        deductions += 12
    if checklist.get("bad_smell", False):
        deductions += 8
    if checklist.get("pests_seen", False):
        deductions += 15
    if checklist.get("dirty_utensils", False):
        deductions += 10
    if checklist.get("food_adulteration", False):
        deductions += 20

    # Inspector audit deductions
    if not checklist.get("food_storage_safe", True):
        deductions += 10
    if not checklist.get("temperature_control", True):
        deductions += 10
    if checklist.get("cross_contamination", False):
        deductions += 12
    if not checklist.get("ingredient_quality", True):
        deductions += 10
    if not checklist.get("kitchen_sanitation", True):
        deductions += 10
    if not checklist.get("waste_disposal", True):
        deductions += 8
    if not checklist.get("water_quality", True):
        deductions += 10
    if checklist.get("pest_control_fail", False):
        deductions += 12

    score = max(0, min(100, base_score - deductions))
    return score


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")


@app.route("/hotels", methods=["GET"])
def get_hotels():
    hotels = load_hotels()
    return jsonify(hotels)


@app.route("/hotel/<int:hotel_id>", methods=["GET"])
def get_hotel(hotel_id):
    hotels = load_hotels()
    hotel = next((h for h in hotels if h["id"] == hotel_id), None)
    if not hotel:
        return jsonify({"error": "Hotel not found"}), 404

    # Attach nearby better options
    if hotel["base_score"] < 60:
        better = [
            h for h in hotels
            if h["base_score"] > hotel["base_score"] and h["id"] != hotel_id
        ]
        better = sorted(better, key=lambda x: x["base_score"], reverse=True)[:3]
        hotel["better_nearby"] = better
    else:
        hotel["better_nearby"] = []

    return jsonify(hotel)


@app.route("/submit_report", methods=["POST"])
def submit_report():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    hotel_id = data.get("hotel_id")
    mode = data.get("mode")  # "customer" or "inspector"
    checklist = data.get("checklist", {})
    notes = data.get("notes", "")

    hotels = load_hotels()
    hotel = next((h for h in hotels if h["id"] == hotel_id), None)
    if not hotel:
        return jsonify({"error": "Hotel not found"}), 404

    # Calculate new score
    new_score = calculate_score(hotel["base_score"], checklist)

    # Adulteration flag
    adulteration_reported = checklist.get("food_adulteration", False)
    if adulteration_reported:
        for h in hotels:
            if h["id"] == hotel_id:
                h["adulteration_flag"] = True
        save_hotels(hotels)

    # Refund trigger conditions
    refund_triggers = []
    if checklist.get("food_adulteration"):
        refund_triggers.append("suspected food adulteration")
    if checklist.get("bad_smell"):
        refund_triggers.append("bad smell reported")
    if checklist.get("foreign_object"):
        refund_triggers.append("foreign object in food")
    if checklist.get("food_poisoning"):
        refund_triggers.append("food poisoning reported")

    # Build report
    report = {
        "report_id": "CS-" + str(uuid.uuid4())[:8].upper(),
        "hotel_id": hotel_id,
        "hotel_name": hotel["name"],
        "mode": mode,
        "checklist": checklist,
        "score": new_score,
        "notes": notes,
        "adulteration_reported": adulteration_reported,
        "refund_triggers": refund_triggers,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    reports = load_reports()
    reports.append(report)
    save_reports(reports)

    # Update hotel base_score with rolling average
    old_score = hotel["base_score"]
    hotel["base_score"] = round((old_score + new_score) / 2)
    save_hotels(hotels)

    return jsonify({
        "success": True,
        "report_id": report["report_id"],
        "score": new_score,
        "adulteration_reported": adulteration_reported,
        "refund_triggers": refund_triggers
    })


@app.route("/report/<report_id>", methods=["GET"])
def get_report(report_id):
    reports = load_reports()
    report = next((r for r in reports if r["report_id"] == report_id), None)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    return jsonify(report)


if __name__ == "__main__":
    print("\n CivicShield is running!")
    print(" Open http://localhost:5000 in your browser\n")
    app.run(debug=True, port=5000)
