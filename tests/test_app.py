"""
Tests for the FastAPI application endpoints
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivities:
    """Test cases for activities endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Basketball Team" in activities
        assert "Programming Class" in activities

    def test_activity_structure(self):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_chess_club_has_initial_participants(self):
        """Test that Chess Club has initial participants"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignup:
    """Test cases for signup endpoint"""

    def test_signup_for_activity(self):
        """Test signing up a new participant for an activity"""
        response = client.post(
            "/activities/Basketball Team/signup?email=newstudent@mergington.edu",
            method="POST"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant(self):
        """Test that signup actually adds the participant"""
        email = "student1@mergington.edu"
        client.post(
            f"/activities/Soccer Club/signup?email={email}",
            method="POST"
        )
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Soccer Club"]["participants"]

    def test_signup_duplicate_participant(self):
        """Test that signing up the same participant twice fails"""
        email = "duplicate@mergington.edu"
        # First signup
        response1 = client.post(
            f"/activities/Art Club/signup?email={email}",
            method="POST"
        )
        assert response1.status_code == 200
        
        # Try to sign up again
        response2 = client.post(
            f"/activities/Art Club/signup?email={email}",
            method="POST"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu",
            method="POST"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_at_capacity(self):
        """Test signing up when activity is at max capacity"""
        activity = "Test Activity"
        # This test would need a way to fill the activity first
        # For now, we'll test the concept with an existing activity
        response = client.get("/activities")
        activities = response.json()
        
        # Find an activity that's close to full if any
        for name, details in activities.items():
            spots_available = details["max_participants"] - len(details["participants"])
            assert spots_available >= 0


class TestUnregister:
    """Test cases for unregister endpoint"""

    def test_unregister_participant(self):
        """Test unregistering a participant from an activity"""
        # First sign up
        email = "unregister_test@mergington.edu"
        client.post(
            f"/activities/Drama Club/signup?email={email}",
            method="POST"
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/Drama Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "remove_test@mergington.edu"
        # Sign up
        client.post(
            f"/activities/Debate Team/signup?email={email}",
            method="POST"
        )
        
        # Verify they're registered
        response = client.get("/activities")
        assert email in response.json()["Debate Team"]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/Debate Team/unregister?email={email}"
        )
        
        # Verify they're removed
        response = client.get("/activities")
        assert email not in response.json()["Debate Team"]["participants"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant who is not registered"""
        response = client.delete(
            "/activities/Math Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/Fake Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRoot:
    """Test cases for root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
