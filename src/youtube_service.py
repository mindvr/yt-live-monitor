"""
YouTube service module for YouTube Livestream Checker.

This module implements the core business logic for checking
if a YouTube channel is currently livestreaming.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

from .channel_parser import extract_channel_id_from_url, check_channel_live_status, ParsingError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeService:
    """
    Service for checking if YouTube channels are currently livestreaming.
    """

    @staticmethod
    def get_channel_id(input_value: str) -> str:
        """
        Get a channel ID from various input formats.

        Args:
            input_value: Channel ID, URL, or handle

        Returns:
            str: The channel ID

        Raises:
            ParsingError: If the channel ID can't be extracted
        """
        return extract_channel_id_from_url(input_value)

    @staticmethod
    def check_if_live(channel_id_or_url: str) -> Dict[str, Any]:
        """
        Check if a channel is currently livestreaming.

        Args:
            channel_id_or_url: Channel ID, URL, or handle

        Returns:
            dict: A result dictionary containing:
                - channel_id: The channel ID that was checked
                - is_live: Whether the channel is currently livestreaming
                - livestream_url: The URL of the livestream (if live)
                - error: Error message (if applicable)
                - checked_at: Timestamp of when the check was performed
        """
        result = {
            "checked_at": datetime.now(timezone.utc).isoformat() + "Z"
        }

        try:
            # First, try to extract or validate the channel ID
            channel_id = extract_channel_id_from_url(channel_id_or_url)
            result["channel_id"] = channel_id

            # Then check if the channel is live
            is_live, livestream_url, title, error = check_channel_live_status(channel_id)

            result["is_live"] = is_live

            if livestream_url:
                result["livestream_url"] = livestream_url

            if title:
                result["title"] = title

            if error:
                result["error"] = error

            return result

        except ParsingError as e:
            logger.error(f"Parsing error: {e}")
            # If we couldn't extract the channel ID, include the original input
            result["channel_id_or_url"] = channel_id_or_url
            result["is_live"] = False
            result["error"] = str(e)
            return result

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            result["channel_id_or_url"] = channel_id_or_url
            result["is_live"] = False
            result["error"] = f"Unexpected error: {str(e)}"
            return result
