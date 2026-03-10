"""
Test suite for the Mergington High School Activities API

Tests follow the AAA (Arrange-Act-Assert) pattern with clear section separation.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Fixture providing a test client for the FastAPI application.
    
    This allows testing HTTP endpoints without running a server.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities to their initial state before each test.
    
    This ensures test isolation and prevents state leakage between tests.
    """
    # Store original state
    original_state = {
        key: {
            "description": value["description"],
            "schedule": value["schedule"],
            "max_participants": value["max_participants"],
            "participants": value["participants"].copy()
        }
        for key, value in activities.items()
    }
    
    yield
    
    # Restore original state after test
    activities.clear()
    activities.update(original_state)


class TestGetActivities:
    """Test suite for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities in the database"""
        
        # Arrange
        # No setup needed - activities already exist in app
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_required_fields(self, client, reset_activities):
        """Test that each activity has all required fields"""
        
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert all(field in activity_data for field in required_fields), \
                f"Activity '{activity_name}' missing required fields"


class TestSignupForActivity:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully_adds_participant(self, client, reset_activities):
        """Test that a student can successfully sign up for an activity"""
        
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_fails_for_nonexistent_activity(self, client, reset_activities):
        """Test that signing up for a non-existent activity returns 404"""
        
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_fails_for_duplicate_email(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students_in_sequence(self, client, reset_activities):
        """Test that multiple different students can sign up for the same activity"""
        
        # Arrange
        activity_name = "Science Club"
        students = [
            "alice@mergington.edu",
            "bobby@mergington.edu",
            "charlie@mergington.edu"
        ]
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        for email in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            # Assert each signup succeeds
            assert response.status_code == 200
        
        # Assert
        assert len(activities[activity_name]["participants"]) == initial_count + 3
        for email in students:
            assert email in activities[activity_name]["participants"]


class TestRemoveFromActivity:
    """Test suite for DELETE /activities/{activity_name}/signup endpoint"""
    
    def test_remove_successfully_unenrolls_participant(self, client, reset_activities):
        """Test that a student can successfully be removed from an activity"""
        
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already enrolled
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Removed {email} from {activity_name}"
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1
    
    def test_remove_fails_for_nonexistent_activity(self, client, reset_activities):
        """Test that removing from a non-existent activity returns 404"""
        
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_fails_for_student_not_enrolled(self, client, reset_activities):
        """Test that removing a student not enrolled in an activity returns 404"""
        
        # Arrange
        activity_name = "Drama Club"
        email = "notstudent@mergington.edu"  # Not enrolled
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not signed up" in response.json()["detail"]
