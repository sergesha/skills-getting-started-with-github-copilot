"""
Tests for the High School Management System API

This module contains pytest tests for all API endpoints including:
- GET /activities - List all activities
- POST /activities/{activity_name}/signup - Sign up for an activity
- DELETE /activities/{activity_name}/unregister - Unregister from an activity
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    activities.clear()
    activities.update({
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
        "Soccer Team": {
            "description": "Competitive soccer training and matches",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 18,
            "participants": ["ryan@mergington.edu", "lisa@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Pick-up games, drills, and intramural tournaments",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": ["mark@mergington.edu", "nina@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["hazel@mergington.edu", "aaron@mergington.edu"]
        },
        "Theater Club": {
            "description": "Acting, stagecraft, and production of school plays",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu", "tom@mergington.edu"]
        },
        "Debate Team": {
            "description": "Practice argumentation, public speaking, and competitions",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["sara@mergington.edu", "leo@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Hands-on STEM challenges and interschool competitions",
            "schedule": "Tuesdays, 3:30 PM - 5:30 PM",
            "max_participants": 24,
            "participants": ["maria@mergington.edu", "kevin@mergington.edu"]
        }
    })


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static_index(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_proper_structure(self, client):
        """Test that each activity has the expected structure"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self, client):
        """Test successful signup of a new student"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Signed up newstudent@mergington.edu for Chess Club"
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_for_nonexistent_activity_fails(self, client):
        """Test that signing up for a nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_signup_duplicate_student_fails(self, client):
        """Test that signing up a student who is already registered fails"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"

    def test_signup_multiple_students_to_same_activity(self, client):
        """Test signing up multiple students to the same activity"""
        # First signup
        response1 = client.post(
            "/activities/Chess Club/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(
            "/activities/Chess Club/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "student1@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "student2@mergington.edu" in activities_data["Chess Club"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_student_success(self, client):
        """Test successful unregistration of an existing student"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Unregistered michael@mergington.edu from Chess Club"
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from a nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"

    def test_unregister_student_not_signed_up_fails(self, client):
        """Test that unregistering a student who is not signed up fails"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notsignedup@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student not signed up for this activity"

    def test_signup_then_unregister_workflow(self, client):
        """Test the complete workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        
        # Sign up
        signup_response = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signed up
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Programming Class"]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/Programming Class/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Programming Class"]["participants"]


class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_activity_name_with_spaces_url_encoded(self, client):
        """Test that activity names with spaces work when URL encoded"""
        # FastAPI/TestClient handles URL encoding automatically
        response = client.post(
            "/activities/Chess Club/signup?email=encoded@mergington.edu"
        )
        assert response.status_code == 200

    def test_email_validation_accepts_valid_format(self, client):
        """Test that valid email formats are accepted"""
        valid_emails = [
            "test@mergington.edu",
            "first.last@mergington.edu",
            "student123@mergington.edu"
        ]
        for email in valid_emails:
            response = client.post(f"/activities/Art Club/signup?email={email}")
            assert response.status_code == 200
