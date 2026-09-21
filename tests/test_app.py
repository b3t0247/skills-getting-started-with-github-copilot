from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def test_client():
    original_activities = deepcopy(app_module.activities)
    with TestClient(app_module.app) as test_client:
        yield test_client
    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_get_activities_returns_activity_collection(test_client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = test_client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert "participants" in response.json()[expected_activity]


def test_signup_adds_participant_to_activity(test_client):
    # Arrange
    activity_name = "Soccer Club"
    email = "new.student@example.com"

    # Act
    response = test_client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in app_module.activities[activity_name]["participants"]


def test_duplicate_signup_returns_bad_request(test_client):
    # Arrange
    activity_name = "Chess Club"
    email = app_module.activities[activity_name]["participants"][0]

    # Act
    response = test_client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities[activity_name]["participants"].count(email) == 1


def test_signup_for_unknown_activity_returns_not_found(test_client):
    # Arrange
    activity_name = "Unknown Club"
    email = "new.student@example.com"

    # Act
    response = test_client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_from_activity(test_client):
    # Arrange
    activity_name = "Soccer Club"
    email = "registered.student@example.com"
    app_module.activities[activity_name]["participants"].append(email)

    # Act
    response = test_client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Removed {email} from {activity_name}"
    }
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_not_found(test_client):
    # Arrange
    activity_name = "Soccer Club"
    email = "missing.student@example.com"

    # Act
    response = test_client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == (
        f"{email} is not signed up for {activity_name}"
    )


def test_unregister_from_unknown_activity_returns_not_found(test_client):
    # Arrange
    activity_name = "Unknown Club"
    email = "registered.student@example.com"

    # Act
    response = test_client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
