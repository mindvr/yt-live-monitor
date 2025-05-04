"""
Tests for the youtube_service module.
"""
import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.youtube_service import YouTubeService, ParsingError


class TestYouTubeService:
    """Tests for the YouTubeService class."""

    @patch('src.youtube_service.extract_channel_id_from_url')
    def test_get_channel_id(self, mock_extract):
        """Test getting a channel ID."""
        mock_extract.return_value = "UCj-Xm8j6WBgKY8OG7s9r2vQ"

        # Test with a channel ID
        channel_id = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        result = YouTubeService.get_channel_id(channel_id)
        assert result == channel_id

        # Test with a URL
        url = "https://www.youtube.com/@RailCowGirl"
        result = YouTubeService.get_channel_id(url)
        assert result == "UCj-Xm8j6WBgKY8OG7s9r2vQ"

    @patch('src.youtube_service.extract_channel_id_from_url')
    @patch('src.youtube_service.check_channel_live_status')
    def test_check_if_live_success(self, mock_check, mock_extract):
        """Test checking if a channel is live when the check succeeds."""
        # Setup the mocks
        mock_extract.return_value = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        mock_check.return_value = (True, "https://www.youtube.com/watch?v=czoEAKX9aaM", None)

        # Perform the check
        result = YouTubeService.check_if_live("UCj-Xm8j6WBgKY8OG7s9r2vQ")

        # Verify the result
        assert result["channel_id"] == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        assert result["is_live"] is True
        assert result["livestream_url"] == "https://www.youtube.com/watch?v=czoEAKX9aaM"
        assert "error" not in result
        assert "checked_at" in result

        # Verify the mocks were called
        mock_extract.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")
        mock_check.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")

    @patch('src.youtube_service.extract_channel_id_from_url')
    @patch('src.youtube_service.check_channel_live_status')
    def test_check_if_live_not_live(self, mock_check, mock_extract):
        """Test checking if a channel is live when it's not."""
        # Setup the mocks
        mock_extract.return_value = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        mock_check.return_value = (False, None, None)

        # Perform the check
        result = YouTubeService.check_if_live("UCj-Xm8j6WBgKY8OG7s9r2vQ")

        # Verify the result
        assert result["channel_id"] == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        assert result["is_live"] is False
        assert "livestream_url" not in result
        assert "error" not in result
        assert "checked_at" in result

        # Verify the mocks were called
        mock_extract.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")
        mock_check.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")

    @patch('src.youtube_service.extract_channel_id_from_url')
    @patch('src.youtube_service.check_channel_live_status')
    def test_check_if_live_with_error(self, mock_check, mock_extract):
        """Test checking if a channel is live when there's an error."""
        # Setup the mocks
        mock_extract.return_value = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        mock_check.return_value = (False, None, "Test error")

        # Perform the check
        result = YouTubeService.check_if_live("UCj-Xm8j6WBgKY8OG7s9r2vQ")

        # Verify the result
        assert result["channel_id"] == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        assert result["is_live"] is False
        assert "livestream_url" not in result
        assert result["error"] == "Test error"
        assert "checked_at" in result

        # Verify the mocks were called
        mock_extract.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")
        mock_check.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")

    @patch('src.youtube_service.extract_channel_id_from_url')
    def test_check_if_live_extraction_error(self, mock_extract):
        """Test checking if a channel is live when channel ID extraction fails."""
        # Setup the mocks
        mock_extract.side_effect = ParsingError("Test parsing error")

        # Perform the check
        result = YouTubeService.check_if_live("invalid-input")

        # Verify the result
        assert "channel_id" not in result
        assert result["channel_id_or_url"] == "invalid-input"
        assert result["is_live"] is False
        assert result["error"] == "Test parsing error"
        assert "checked_at" in result

        # Verify the mocks were called
        mock_extract.assert_called_once_with("invalid-input")

    @patch('src.youtube_service.extract_channel_id_from_url')
    @patch('src.youtube_service.check_channel_live_status')
    def test_check_if_live_unexpected_error(self, mock_check, mock_extract):
        """Test checking if a channel is live when there's an unexpected error."""
        # Setup the mocks
        mock_extract.return_value = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        mock_check.side_effect = Exception("Test unexpected error")

        # Perform the check
        result = YouTubeService.check_if_live("UCj-Xm8j6WBgKY8OG7s9r2vQ")

        # Verify the result
        assert result["channel_id"] == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        assert result["is_live"] is False
        assert "livestream_url" not in result
        assert "Test unexpected error" in result["error"]
        assert "checked_at" in result

        # Verify the mocks were called
        mock_extract.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")
        mock_check.assert_called_once_with("UCj-Xm8j6WBgKY8OG7s9r2vQ")