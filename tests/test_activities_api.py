import uuid
import urllib.parse

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def create_unique_email() -> str:
    return f"student+{uuid.uuid4().hex[:8]}@mergington.edu"


def encode_email(email: str) -> str:
    return urllib.parse.quote(email, safe="")


def test_get_activities_returns_activity_data():
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity_name in data
    assert "description" in data[expected_activity_name]
    assert "participants" in data[expected_activity_name]
    assert isinstance(data[expected_activity_name]["participants"], list)


def test_signup_adds_participant_to_activity():
    # Arrange
    email = create_unique_email()
    activity_name = "Programming Class"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={encode_email(email)}"
    )
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in participants


def test_unregister_removes_participant_from_activity():
    # Arrange
    email = create_unique_email()
    activity_name = "Gym Class"
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={encode_email(email)}"
    )
    assert signup_response.status_code == 200

    # Act
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={encode_email(email)}"
    )
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]

    # Assert
    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in participants


def test_signup_duplicate_email_returns_400():
    # Arrange
    email = create_unique_email()
    activity_name = "Drama Club"
    first_response = client.post(
        f"/activities/{activity_name}/signup?email={encode_email(email)}"
    )
    assert first_response.status_code == 200

    # Act
    duplicate_response = client.post(
        f"/activities/{activity_name}/signup?email={encode_email(email)}"
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_missing_participant_returns_404():
    # Arrange
    email = create_unique_email()
    activity_name = "Basketball Team"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister?email={encode_email(email)}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unknown_activity_returns_404_for_signup_and_unregister():
    # Arrange
    email = create_unique_email()
    activity_name = "Nonexistent Club"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={encode_email(email)}"
    )
    unregister_response = client.delete(
        f"/activities/{activity_name}/unregister?email={encode_email(email)}"
    )

    # Assert
    assert signup_response.status_code == 404
    assert signup_response.json()["detail"] == "Activity not found"
    assert unregister_response.status_code == 404
    assert unregister_response.json()["detail"] == "Activity not found"
