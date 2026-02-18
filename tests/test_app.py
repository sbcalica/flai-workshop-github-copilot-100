"""
Test suite for Mergington High School API

Tests all endpoints for the FastAPI application that manages
extracurricular activities.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball practice and inter-school games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu", "lucas@mergington.edu"]
        },
        "Track and Field": {
            "description": "Running, jumping, and throwing events for all skill levels",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, improvisation, and theater productions",
            "schedule": "Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["liam@mergington.edu", "charlotte@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ethan@mergington.edu", "amelia@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "STEM competitions covering biology, chemistry, physics, and engineering",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["benjamin@mergington.edu", "harper@mergington.edu"]
        }
    }
    
    # Reset activities before test
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test getting all activities returns complete list"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball Team" in data
    
    def test_activities_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        # Check Chess Club structure
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
    
    def test_activities_have_participants(self, client):
        """Test that activities contain participant information"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for the signup endpoint"""
    
    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for Chess Club"
        
        # Verify the student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for activity that doesn't exist returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_duplicate_student(self, client):
        """Test that duplicate signup is prevented"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_multiple_students_same_activity(self, client):
        """Test multiple new students can sign up for the same activity"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                "/activities/Chess Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all students were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Chess Club"]["participants"]
        for email in emails:
            assert email in participants
    
    def test_signup_different_activities(self, client):
        """Test signing up for multiple different activities"""
        email = "multi@mergington.edu"
        
        activities_to_join = ["Chess Club", "Programming Class", "Art Studio"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify student is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint"""
    
    def test_unregister_from_activity_success(self, client):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Unregistered {email} from Chess Club"
        
        # Verify the student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregister from activity that doesn't exist returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_unregister_student_not_in_activity(self, client):
        """Test unregistering student who isn't signed up returns 400"""
        email = "notin@mergington.edu"
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is not signed up for this activity"
    
    def test_signup_then_unregister(self, client):
        """Test complete workflow: signup then unregister"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Step 1: Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity]["participants"]
        
        # Step 2: Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity]["participants"]
    
    def test_unregister_multiple_times_fails(self, client):
        """Test that unregistering twice fails on second attempt"""
        email = "michael@mergington.edu"
        
        # First unregister should succeed
        response1 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert response2.json()["detail"] == "Student is not signed up for this activity"


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_activity_membership_persistence(self, client):
        """Test that activity memberships persist across multiple operations"""
        email = "persistent@mergington.edu"
        
        # Initial signup
        client.post("/activities/Drama Club/signup", params={"email": email})
        
        # Perform operations on other activities
        client.post("/activities/Basketball Team/signup", params={"email": "other@mergington.edu"})
        client.get("/activities")
        
        # Verify original signup still exists
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Drama Club"]["participants"]
    
    def test_multiple_activities_independent(self, client):
        """Test that operations on one activity don't affect others"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Add students to different activities
        client.post("/activities/Chess Club/signup", params={"email": email1})
        client.post("/activities/Art Studio/signup", params={"email": email2})
        
        # Remove from one activity
        client.delete("/activities/Chess Club/unregister", params={"email": email1})
        
        # Verify other activity unchanged
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email1 not in activities_data["Chess Club"]["participants"]
        assert email2 in activities_data["Art Studio"]["participants"]
