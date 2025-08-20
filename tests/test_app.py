import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import pytest
from app import app, NOTIFICATIONS


# Sorgt dafür, dass die In-Memory-Liste NOTIFICATIONS vor und nach jedem Test geleert wird
@pytest.fixture(autouse=True)
def _clear_state():
    NOTIFICATIONS.clear()
    yield
    NOTIFICATIONS.clear()

# Erstellt einen Flask-Test-Client, um HTTP-Anfragen in Tests ohne echten Server zu simulieren
@pytest.fixture
def client():
    return app.test_client()

# Test: Warning-Benachrichtigung wird gespeichert und erfolgreich an ntfy weitergeleitet
def test_warning_forwarded(monkeypatch, client): 
    called = {"count": 0}

    class DummyResponse:
        status_code = 200

    def fake_post(*args, **kwargs):
        called["count"] += 1
        return DummyResponse()

    import app as app_module
    monkeypatch.setattr(app_module.requests, "post", fake_post)

    payload = {
        "Type": "Warning",
        "Name": "Backup Failure",
        "Description": "The backup failed due to a database problem",
    }
    resp = client.post("/notifications", json=payload)
    assert resp.status_code == 202
    assert resp.get_json()["status"] == "forwarded"
    assert called["count"] == 1
    assert len(NOTIFICATIONS) == 1
    assert NOTIFICATIONS[0]["forwarded"] is True

# Test: Info-Benachrichtigung wird gespeichert, aber NICHT an ntfy weitergeleitet
def test_info_not_forwarded(monkeypatch, client):
    called = {"count": 0}

    class DummyResponse:
        status_code = 200

    def fake_post(*args, **kwargs):
        called["count"] += 1
        return DummyResponse()

    import app as app_module
    monkeypatch.setattr(app_module.requests, "post", fake_post)

    payload = {
        "Type": "Info", #Info-Nachricht soll NICHT weitergeleitet werden
        "Name": "Quota Exceeded",
        "Description": "Compute Quota exceeded",
    }
    resp = client.post("/notifications", json=payload)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ignored"
    assert called["count"] == 0
    assert len(NOTIFICATIONS) == 1
    assert NOTIFICATIONS[0]["forwarded"] is False

# Test: ungültiger Nachrichtentyp (Type ist weder Warning noch Info)
def test_invalid_type(client):
    payload = {"Type": "Error", "Name": "X", "Description": "Y"}
    resp = client.post("/notifications", json=payload)
    assert resp.status_code == 400
    assert "Unsupported" in resp.get_json()["error"]

# Test: fehlende Pflichtfelder (hier: Description fehlt)
def test_missing_fields(client):
    resp = client.post("/notifications", json={"Type": "Warning", "Name": "OnlyName"})
    assert resp.status_code == 400
    assert "Missing field" in resp.get_json()["error"]

# Test: fehlerhaftes JSON (kein gültiges JSON übermittelt)
def test_malformed_json(client):
    resp = client.post("/notifications", data="xyz", headers={"Content-Type": "application/json"})
    assert resp.status_code == 400
    assert "Malformed" in resp.get_json()["error"]

