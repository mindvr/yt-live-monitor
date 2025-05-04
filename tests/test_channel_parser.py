"""
Tests for the channel_parser module.
"""
import os
import sys
from unittest.mock import patch, MagicMock

import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.channel_parser import (
    extract_channel_id_from_url,
    fetch_channel_id_from_web,
    parse_channel_page,
    check_channel_live_status,
    ParsingError
)


class TestChannelParser:
    """Tests for the channel_parser module."""

    def test_extract_channel_id_direct(self):
        """Test extracting a channel ID when it's directly provided."""
        channel_id = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        result = extract_channel_id_from_url(channel_id)
        assert result == channel_id

    def test_extract_channel_id_from_channel_url(self):
        """Test extracting a channel ID from a channel URL."""
        url = "https://www.youtube.com/channel/UCj-Xm8j6WBgKY8OG7s9r2vQ"
        expected_id = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        result = extract_channel_id_from_url(url)
        assert result == expected_id

    @patch('src.channel_parser.fetch_channel_id_from_web')
    def test_extract_channel_id_from_handle(self, mock_fetch):
        """Test extracting a channel ID from a handle."""
        mock_fetch.return_value = "UCj-Xm8j6WBgKY8OG7s9r2vQ"

        # Test with @ prefix
        handle = "@RailCowGirl"
        result = extract_channel_id_from_url(handle)
        assert result == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        mock_fetch.assert_called_with("https://www.youtube.com/@RailCowGirl")

        # Test without @ prefix
        mock_fetch.reset_mock()
        handle = "RailCowGirl"
        result = extract_channel_id_from_url(handle)
        assert result == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        mock_fetch.assert_called_with("https://www.youtube.com/@RailCowGirl")

    @patch('src.channel_parser.requests.get')
    def test_fetch_channel_id_from_web(self, mock_get):
        """Test fetching a channel ID from a web page."""
        # Setup the mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        # Read the example HTML file
        with open('../examples/get-for-channel-id-excerpt.html', 'r') as file:
            mock_response.text = file.read()

        mock_get.return_value = mock_response

        url = "https://www.youtube.com/@RailCowGirl"
        result = fetch_channel_id_from_web(url)

        assert result == "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        mock_get.assert_called_once()

    def test_parse_channel_page_live(self):
        """Test parsing a channel page when the channel is live."""
        # Read the example HTML for a broadcasting channel
        with open('../examples/get-broadcasting-excerpt.html', 'r') as file:
            html_content = file.read()

        result = parse_channel_page(html_content)

        assert result["is_live"] is True
        assert result["livestream_url"] == "https://www.youtube.com/watch?v=czoEAKX9aaM"

    def test_parse_channel_page_not_live(self):
        """Test parsing a channel page when the channel is not live."""
        # Read the example HTML for a non-broadcasting channel
        with open('../examples/get-not-broadcasting-excerpt.html', 'r') as file:
            html_content = file.read()

        result = parse_channel_page(html_content)

        assert result["is_live"] is False
        assert result["livestream_url"] is None

    def test_parse_channel_page_error(self):
        """Test parsing a channel page with invalid HTML."""
        # Create invalid HTML content
        html_content = "<html><head></head><body>No canonical link here</body></html>"

        with pytest.raises(ParsingError):
            parse_channel_page(html_content)

    @patch('src.channel_parser.requests.get')
    def test_check_channel_live_status_live(self, mock_get):
        """Test checking if a channel is live when it is."""
        # Setup the mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        # Read the example HTML file for a broadcasting channel
        with open('../examples/get-broadcasting-excerpt.html', 'r') as file:
            mock_response.text = file.read()

        mock_get.return_value = mock_response

        channel_id = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        is_live, livestream_url, error = check_channel_live_status(channel_id)

        assert is_live is True
        assert livestream_url == "https://www.youtube.com/watch?v=czoEAKX9aaM"
        assert error is None
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0] == f"https://www.youtube.com/channel/{channel_id}/live"
        assert "User-Agent" in mock_get.call_args[1]["headers"]

    @patch('src.channel_parser.requests.get')
    def test_check_channel_live_status_not_live(self, mock_get):
        """Test checking if a channel is live when it is not."""
        # Setup the mock response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        # Read the example HTML file for a non-broadcasting channel
        with open('../examples/get-not-broadcasting-excerpt.html', 'r') as file:
            mock_response.text = file.read()

        mock_get.return_value = mock_response

        channel_id = "UC101o-vQ2iOj9vr00JUlyKw"
        is_live, livestream_url, error = check_channel_live_status(channel_id)

        assert is_live is False
        assert livestream_url is None
        assert error is None
        mock_get.assert_called_once()
        assert mock_get.call_args[0][0] == f"https://www.youtube.com/channel/{channel_id}/live"
        assert "User-Agent" in mock_get.call_args[1]["headers"]

    @patch('src.channel_parser.requests.get')
    def test_check_channel_live_status_request_error(self, mock_get):
        """Test checking if a channel is live when there's a request error."""
        # Setup the mock to raise an exception
        mock_get.side_effect = Exception("Test request error")

        channel_id = "UCj-Xm8j6WBgKY8OG7s9r2vQ"
        is_live, livestream_url, error = check_channel_live_status(channel_id)

        assert is_live is False
        assert livestream_url is None
        assert error is not None
        assert "Test request error" in error
