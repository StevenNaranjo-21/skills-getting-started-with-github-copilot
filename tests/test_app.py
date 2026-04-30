from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
INITIAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state before each test."""
    app_module.activities = deepcopy(INITIAL_ACTIVITIES)
    yield


def test_get_activities_returns_available_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity in data
    assert isinstance(data[expected_activity], dict)


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "test.student@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={new_email}"
    )
    activities_response = client.get("/activities")
    activities_data = activities_response.json()

    # Assert
    assert signup_response.status_code == 200
    assert new_email in activities_data[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={duplicate_email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_participant_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    delete_response = client.delete(
        f"/activities/{activity_name}/participants?email={existing_email}"
    )
    activities_response = client.get("/activities")
    activities_data = activities_response.json()

    # Assert
    assert delete_response.status_code == 200
    assert existing_email not in activities_data[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants?email={missing_email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_for_missing_activity_returns_404():
    # Arrange
    missing_activity = "Nonexistent Club"
    email = "ghost.student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{missing_activity}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_for_missing_activity_returns_404():
    # Arrange
    missing_activity = "Nonexistent Club"
    email = "ghost.student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{missing_activity}/participants?email={email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
