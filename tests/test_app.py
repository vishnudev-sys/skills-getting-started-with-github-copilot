from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity keys
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "test_student@example.com"

    # Ensure participant not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        # remove if present for a deterministic test
        del_resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
        assert del_resp.status_code == 200

    # Sign up
    signup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert signup.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

    # Duplicate signup should fail
    dup = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert dup.status_code == 400

    # Unregister
    unreg = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert unreg.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_unregister_missing_participant():
    activity = "Chess Club"
    email = "no_such_student@example.com"
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert resp.status_code == 404
