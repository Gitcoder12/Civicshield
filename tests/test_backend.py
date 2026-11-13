import json

import backend_app


def test_root_serves_checked_in_index():
    backend_app.app.config.update(TESTING=True)
    client = backend_app.app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert b"CivicShield" in response.data


def test_hotels_endpoint_reads_configured_data_file(tmp_path, monkeypatch):
    hotels_file = tmp_path / "hotels.json"
    hotels_file.write_text(json.dumps([{"id": 1, "name": "Example Cafe", "base_score": 80}]))
    monkeypatch.setattr(backend_app, "HOTELS_FILE", str(hotels_file))
    backend_app.app.config.update(TESTING=True)
    client = backend_app.app.test_client()

    response = client.get("/hotels")

    assert response.status_code == 200
    assert response.get_json() == [{"id": 1, "name": "Example Cafe", "base_score": 80}]
