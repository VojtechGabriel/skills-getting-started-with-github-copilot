import importlib

import pytest


@pytest.fixture
def client():
    # Reload the app module to reset in-memory state between tests
    import src.app as app_module
    importlib.reload(app_module)
    from fastapi.testclient import TestClient

    return TestClient(app_module.app)


def test_get_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_adds_participant(client):
    activity = "Basketball Team"
    email = "tester@example.com"

    # Sign up
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant appears in activity
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate_fails(client):
    activity = "Basketball Team"
    email = "duplicate@example.com"

    resp1 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp1.status_code == 200

    resp2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp2.status_code == 400
    assert "already signed up" in resp2.json().get("detail", "").lower()


def test_unregister_participant(client):
    activity = "Basketball Team"
    email = "remove_me@example.com"

    # Sign up first
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200

    # Now unregister
    r2 = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r2.status_code == 200
    assert "Unregistered" in r2.json().get("message", "")

    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
