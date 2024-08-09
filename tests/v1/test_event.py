import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from main import app
from api.v1.models.events import Event
from api.v1.models.user import User
from api.v1.schemas.events import EventCreate
from api.db.database import get_db
from api.v1.services.user import user_service

client = TestClient(app)

@pytest.fixture
def db_session():
    session = MagicMock(spec=Session)
    return session

@pytest.fixture
def superuser():
    user = MagicMock(spec=User)
    user.is_superuser = True
    return user

@pytest.fixture(autouse=True)
def override_get_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    yield
    app.dependency_overrides[get_db] = get_db

@pytest.fixture(autouse=True)
def override_get_current_super_admin(superuser):
    def mock_get_current_super_admin(db: Session, current_user: User):
        return superuser
    
    app.dependency_overrides[user_service.get_current_super_admin] = mock_get_current_super_admin
    yield
    app.dependency_overrides[user_service.get_current_super_admin] = user_service.get_current_super_admin

def test_create_event(db_session, superuser):
    event_data = {
        "title": "Test Event",
        "description": "This is a test event",
        "start_time": "2024-08-01T14:00:00Z",
        "end_time": "2024-08-01T16:00:00Z",
        "location": "123 Event St."
    }

    db_session.add = MagicMock()
    db_session.commit = MagicMock()
    db_session.refresh = MagicMock()
    
    mock_event = MagicMock(spec=Event)
    mock_event.id = 1
    mock_event.title = event_data['title']
    mock_event.description = event_data['description']
    mock_event.start_time = event_data['start_time']
    mock_event.end_time = event_data['end_time']
    mock_event.location = event_data['location']
    db_session.refresh.side_effect = lambda obj: obj.__dict__.update(mock_event.__dict__)

    response = client.post("/api/v1/events/", json=event_data)

    assert response.status_code == 200
    assert response.json() == {
        "id": mock_event.id,
        "title": mock_event.title,
        "description": mock_event.description,
        "start_time": mock_event.start_time,
        "end_time": mock_event.end_time,
        "location": mock_event.location,
        "message": "Event created successfully"
    }

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()
