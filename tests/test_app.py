"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_activities_contain_expected_activities(self):
        """Test that activities include expected entries"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Drama Club",
            "Art Studio",
            "Science Club",
            "Debate Team"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = [
            "description",
            "schedule",
            "max_participants",
            "participants"
        ]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"{activity_name} missing {field}"

    def test_activity_participants_is_list(self):
        """Test that participants field is a list"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name} participants is not a list"


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_for_valid_activity(self):
        """Test signing up for a valid activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_returns_success_message(self):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        data = response.json()
        assert "Signed up" in data["message"]
        assert "test@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_for_nonexistent_activity(self):
        """Test signing up for a non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds the participant to the activity"""
        test_email = "new.participant@mergington.edu"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_participants = response.json()["Programming Class"]["participants"].copy()
        
        # Sign up
        client.post(
            "/activities/Programming Class/signup?email=" + test_email
        )
        
        # Check that participant was added
        response = client.get("/activities")
        updated_participants = response.json()["Programming Class"]["participants"]
        
        assert test_email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1

    def test_signup_with_empty_email(self):
        """Test signup with empty email parameter"""
        response = client.post(
            "/activities/Chess Club/signup?email="
        )
        # Empty email should still be added (not validated in current implementation)
        assert response.status_code == 200

    def test_signup_with_special_characters_in_email(self):
        """Test signup with special characters in email"""
        response = client.post(
            "/activities/Chess Club/signup?email=test+tag@mergington.edu"
        )
        assert response.status_code == 200


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects(self):
        """Test that root endpoint redirects"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivityStructure:
    """Tests for activity data structure"""

    def test_all_activities_have_max_participants(self):
        """Test that all activities have a max_participants count"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "max_participants" in activity_data
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_participants_count_does_not_exceed_max(self):
        """Test that current participant count doesn't exceed max (in initial state)"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert len(activity_data["participants"]) <= activity_data["max_participants"], \
                f"{activity_name} has more participants than max allowed"
