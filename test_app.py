import pytest
from fastapi.testclient import TestClient
from main import app
from database.database import engine, Base
from sqlalchemy.orm import Session
from utils.database_utils import create_user, get_user_by_username
from models.user import User
from schemas.user import UserCreate


# Create a test client
client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    yield engine
    # Cleanup after tests
    Base.metadata.drop_all(bind=engine)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "AI Interview Simulator" in data["message"]


def test_create_user():
    """Test creating a new user"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword"
    }
    
    response = client.post("/api/v1/user/", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


def test_get_user():
    """Test getting a user by ID"""
    # First create a user
    user_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "full_name": "Test User 2",
        "password": "testpassword"
    }
    
    create_response = client.post("/api/v1/user/", json=user_data)
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]
    
    # Now get the user
    response = client.get(f"/api/v1/user/{user_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == user_id
    assert data["username"] == "testuser2"


def test_start_interview():
    """Test starting an interview session"""
    # First create a user
    user_data = {
        "username": "interview_test",
        "email": "interview@example.com",
        "full_name": "Interview Test",
        "password": "testpassword"
    }
    
    create_response = client.post("/api/v1/user/", json=user_data)
    assert create_response.status_code == 200
    user_id = create_response.json()["id"]
    
    # Start an interview
    interview_data = {
        "user_id": user_id,
        "interview_type": "dsa"
    }
    
    response = client.post("/api/v1/interview/start", json=interview_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["user_id"] == user_id
    assert data["interview_type"] == "dsa"
    assert data["status"] == "active"


def test_get_leaderboard():
    """Test getting the leaderboard"""
    response = client.get("/api/v1/leaderboard/")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    # May be empty if no users have scores, but should be a list