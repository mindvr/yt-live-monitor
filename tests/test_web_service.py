"""
Tests for the web_service module.
"""
import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from fastapi.testclient import TestClient

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.web_service import app

client = TestClient(app)


class TestWebService:
    """Tests for the web service API endpoints."""

    def test_get_status(self):
        """Test the /status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "YouTube Livestream Checker"

    @patch('src.web_service.YouTubeService.check_if_live')
    def test_check_live_by_id_success(self, mock_check):
        """Test the /check-live/{channel_id} endpoint when the check succeeds."""
        # Setup the mock
        mock_check.return_value = {
            "channel_id": "UCj-Xm8j6WBgKY8OG7s9r2vQ",
            "is_live": True,
            "livestream_url": "https://www.youtube.com/watch?v=czoEAKX9aaM",
            "checked_at": "2023-09-14T12:34:56Z"
        }

        # Make the request
        response = client.get("/check-live/UCj-Xm8j6WBgKY8OG7s9r2vQ")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        assert data["is_live"] is True
        assert data["livestream_url"] == "https://www.youtube.com/watch?v=czoEAKX9aaM"
        assert data["checked_at"] == "2023-09-14T12:34:56Z"

        # Verify the mock was called
        mock_check.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")

    @patch('src.web_service.YouTubeService.check_if_live')
    def test_check_live_by_id_not_live(self, mock_check):
        """Test the /check-live/{channel_id} endpoint when the channel is not live."""
        # Setup the mock
        mock_check.return_value = {
            "channel_id": "UCj-Xm8j6WBgKY8OG7s9r2vQ",
            "is_live": False,
            "checked_at": "2023-09-14T12:34:56Z"
        }

        # Make the request
        response = client.get("/check-live/UCj-Xm8j6WBgKY8OG7s9r2vQ")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        assert data["is_live"] is False
        assert data["livestream_url"] is None
        assert data["checked_at"] == "2023-09-14T12:34:56Z"

        # Verify the mock was called
        mock_check.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")

    @patch('src.web_service.YouTubeService.check_if_live')
    def test_check_live_by_id_with_error(self, mock_check):
        """Test the /check-live/{channel_id} endpoint when there's an error."""
        # Setup the mock
        mock_check.return_value = {
            "channel_id": "UCj-Xm8j6WBgKY8OG7s9r2vQ",
            "is_live": False,
            "error": "Test error",
            "checked_at": "2023-09-14T12:34:56Z"
        }

        # Make the request
        response = client.get("/check-live/UCj-Xm8j6WBgKY8OG7s9r2vQ")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        assert data["is_live"] is False
        assert data["error"] == "Test error"
        assert data["checked_at"] == "2023-09-14T12:34:56Z"

        # Verify the mock was called
        mock_check.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")

    @patch('src.web_service.YouTubeService.check_if_live')
    def test_check_live_by_id_error_response(self, mock_check):
        """Test the /check-live/{channel_id} endpoint when an exception is raised."""
        # Setup the mock to raise an exception
        mock_check.side_effect = Exception("Test exception")

        # Make the request
        response = client.get("/check-live/UCj-Xm8j6WBgKY8OG7s9r2vQ")

        # Verify the response
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "Test exception"

        # Verify the mock was called
        mock_check.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")

    @patch('src.web_service.YouTubeService.check_if_live')
    def test_check_live_by_url_success(self, mock_check):
        """Test the /check-live POST endpoint when the check succeeds."""
        # Setup the mock
        mock_check.return_value = {
            "channel_id": "UCj-Xm8j6WBgKY8OG7s9r2vQ",
            "is_live": True,
            "livestream_url": "https://www.youtube.com/watch?v=czoEAKX9aaM",
            "checked_at": "2023-09-14T12:34:56Z"
        }

        # Make the request
        response = client.post(
            "/check-live",
            json={"url": "https://www.youtube.com/@RailCowGirl"}
        )

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["channel_id"] == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        assert data["is_live"] is True
        assert data["livestream_url"] == "https://www.youtube.com/watch?v=czoEAKX9aaM"
        assert data["checked_at"] == "2023-09-14T12:34:56Z"

        # Verify the mock was called
        mock_check.assert_called_once_with("https://www.youtube.com/@RailCowGirl")

    @patch('src.web_service.YouTubeService.check_if_live')
    def test_check_live_by_url_error_response(self, mock_check):
        """Test the /check-live POST endpoint when an exception is raised."""
        # Setup the mock to raise an exception
        mock_check.side_effect = Exception("Test exception")

        # Make the request
        response = client.post(
            "/check-live",
            json={"url": "https://www.youtube.com/@RailCowGirl"}
        )

        # Verify the response
        assert response.status_code == 500
        data = response.json()
        assert data["detail"] == "Test exception"

        # Verify the mock was called
        mock_check.assert_called_once_with("https://www.youtube.com/@RailCowGirl")

    def test_check_live_by_url_invalid_request(self):
        """Test the /check-live POST endpoint with an invalid request."""
        # Make a request with invalid JSON
        response = client.post(
            "/check-live",
            json={"invalid_key": "https://www.youtube.com/@RailCowGirl"}
        )

        # Verify the response
        assert response.status_code == 422  # Unprocessable Entity