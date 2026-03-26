import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Keep tests deterministic; state changes will remain in-memory across tests
    # and the suite order is designed to handle the mutation path.
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    # Act
    response = client.get('/activities')
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert 'Chess Club' in data
    assert 'Programming Class' in data
    assert isinstance(data['Chess Club']['participants'], list)


def test_signup_for_activity_adds_participant():
    # Arrange
    email = 'test_user@example.com'
    activity = 'Chess Club'

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert 'Signed up test_user@example.com for Chess Club' in response.json()['message']

    get_response = client.get('/activities')
    assert email in get_response.json()[activity]['participants']


def test_signup_duplicate_returns_400():
    # Arrange
    email = 'test_user@example.com'
    activity = 'Chess Club'

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()['detail'] == 'Student is already signed up for this activity'


def test_remove_participant_success():
    # Arrange
    email = 'test_user@example.com'
    activity = 'Chess Club'

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    assert 'Unregistered test_user@example.com from Chess Club' in response.json()['message']

    get_response = client.get('/activities')
    assert email not in get_response.json()[activity]['participants']


def test_remove_participant_not_found_returns_404():
    # Arrange
    email = 'nonexistent@example.com'
    activity = 'Chess Club'

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    assert response.json()['detail'] == 'Participant not found in activity'


def test_activity_not_found_returns_404_on_signup():
    # Arrange
    activity = 'NoSuchClub'

    # Act
    response = client.post(f"/activities/{activity}/signup?email=test@example.com")

    # Assert
    assert response.status_code == 404
    assert response.json()['detail'] == 'Activity not found'


def test_activity_not_found_returns_404_on_delete():
    # Arrange
    activity = 'NoSuchClub'

    # Act
    response = client.delete(f"/activities/{activity}/participants/test@example.com")

    # Assert
    assert response.status_code == 404
    assert response.json()['detail'] == 'Activity not found'
