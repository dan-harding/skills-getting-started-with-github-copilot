from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    response = client.post(
        "/activities/Chess Club/signup?email=student@example.com"
    )
    assert response.status_code == 200

    delete_response = client.delete(
        "/activities/Chess Club/unregister?email=student@example.com"
    )
    assert delete_response.status_code == 200

    activities_response = client.get("/activities")
    activity = activities_response.json()["Chess Club"]
    assert "student@example.com" not in activity["participants"]
