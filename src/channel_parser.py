"""
Channel parser module for YouTube Livestream Checker.

This module handles the parsing of YouTube channel URLs and HTML responses
to extract channel IDs and determine if a channel is currently livestreaming.
"""
import re
import logging
from typing import Optional, Tuple, Dict, Any
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants for URL patterns
YOUTUBE_DOMAIN = "youtube.com"
YOUTUBE_SHORT_DOMAIN = "youtu.be"
CHANNEL_ID_PATTERN = r"UC[a-zA-Z0-9_-]{22}"
VIDEO_ID_PATTERN = r"[a-zA-Z0-9_-]{11}"


class ParsingError(Exception):
    """Exception raised when parsing YouTube channel data fails."""
    pass


def extract_channel_id_from_url(url: str) -> str:
    """
    Extract a YouTube channel ID from various URL formats.

    Args:
        url: A YouTube URL that could be in various formats
             (channel URL, handle, custom URL, etc.)

    Returns:
        str: The channel ID in the format 'UCxxxxxxxxxxxxxxxxxxxxxxxx'

    Raises:
        ParsingError: If the channel ID cannot be extracted or the URL is invalid
    """
    url = url.strip()

    # Check if the input is already a channel ID
    if re.match(f"^{CHANNEL_ID_PATTERN}$", url):
        return url

    # Handle URLs with channel ID already in them
    channel_id_match = re.search(f"{CHANNEL_ID_PATTERN}", url)
    if channel_id_match:
        return channel_id_match.group(0)

    # Handle different URL formats
    try:
        # Handle @username format
        if url.startswith('@'):
            full_url = f"https://www.youtube.com/{url}"
            return fetch_channel_id_from_web(full_url)

        # Handle youtube.com/@username format
        if YOUTUBE_DOMAIN in url and '@' in url:
            return fetch_channel_id_from_web(url)

        # Handle youtube.com/c/CustomName format
        if YOUTUBE_DOMAIN in url and '/c/' in url:
            return fetch_channel_id_from_web(url)

        # Handle youtube.com/user/Username format
        if YOUTUBE_DOMAIN in url and '/user/' in url:
            return fetch_channel_id_from_web(url)

        # Handle any other YouTube URL that might lead to a channel
        if YOUTUBE_DOMAIN in url or YOUTUBE_SHORT_DOMAIN in url:
            return fetch_channel_id_from_web(url)

        # If we reach here with a non-URL string, try it as a handle
        if not url.startswith(('http://', 'https://')):
            handle = url if url.startswith('@') else f"@{url}"
            full_url = f"https://www.youtube.com/{handle}"
            return fetch_channel_id_from_web(full_url)

        raise ParsingError(f"Could not parse channel ID from: {url}")

    except requests.RequestException as e:
        logger.error(f"Request error while fetching channel ID: {e}")
        raise ParsingError(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Error extracting channel ID from {url}: {e}")
        raise ParsingError(f"Failed to extract channel ID: {str(e)}")


def fetch_channel_id_from_web(url: str) -> str:
    """
    Fetch a web page and extract the channel ID from the canonical link.

    Args:
        url: The URL to fetch the channel page from

    Returns:
        str: The extracted channel ID

    Raises:
        ParsingError: If the channel ID can't be extracted from the page
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')

    # Look for canonical link which usually contains the channel ID
    canonical_link = soup.find('link', rel='canonical')

    if not canonical_link or not canonical_link.get('href'):
        raise ParsingError(f"Could not find canonical link in {url}")

    canonical_url = canonical_link['href']

    # Extract channel ID from canonical URL
    channel_id_match = re.search(f"{CHANNEL_ID_PATTERN}", canonical_url)
    if channel_id_match:
        return channel_id_match.group(0)

    # If we can't find a channel ID, this might be a video page
    # In this case, we need to extract the channel ID from other elements
    # This would require more complex parsing which is outside the scope of this function
    raise ParsingError(f"Could not extract channel ID from {canonical_url}")


def parse_channel_page(html_content: str) -> Dict[str, Any]:
    """
    Parse a YouTube channel page to determine if it's currently livestreaming.

    Args:
        html_content: The HTML content of the channel page

    Returns:
        dict: A dictionary containing:
            - is_live (bool): Whether the channel is currently livestreaming
            - livestream_url (str, optional): The URL of the livestream if the channel is live
            - title (str, optional): The title of the livestream if the channel is live
            - error (str, optional): Error message if parsing failed

    Raises:
        ParsingError: If the HTML cannot be parsed
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        canonical_link = soup.find('link', rel='canonical')

        if not canonical_link or not canonical_link.get('href'):
            raise ParsingError("Could not find canonical link in channel page")

        canonical_url = canonical_link['href']

        # Check if the canonical URL is a video URL (indicating a livestream)
        video_id_match = re.search(r"youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})", canonical_url)

        if video_id_match:
            video_id = video_id_match.group(1)

            # Extract the title from the meta tag
            title = None
            meta_title = soup.find('meta', attrs={'name': 'title'})
            if meta_title and meta_title.get('content'):
                title = meta_title['content']

            return {
                "is_live": True,
                "livestream_url": f"https://www.youtube.com/watch?v={video_id}",
                "title": title
            }
        else:
            # If the canonical URL points back to the channel, it's not livestreaming
            return {
                "is_live": False,
                "livestream_url": None,
                "title": None
            }

    except Exception as e:
        logger.error(f"Error parsing channel page: {e}")
        raise ParsingError(f"Failed to parse channel page: {str(e)}")


def check_channel_live_status(channel_id: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Check if a YouTube channel is currently livestreaming.

    Args:
        channel_id: The YouTube channel ID to check

    Returns:
        Tuple[bool, Optional[str], Optional[str], Optional[str]]:
            - is_live: Whether the channel is currently livestreaming
            - livestream_url: The URL of the livestream if the channel is live
            - title: The title of the livestream if the channel is live
            - error: Error message if checking failed
    """
    try:
        # Construct the /live URL for the channel
        live_url = f"https://www.youtube.com/channel/{channel_id}/live"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(live_url, headers=headers)
        response.raise_for_status()

        result = parse_channel_page(response.text)
        return result["is_live"], result.get("livestream_url"), result.get("title"), None

    except requests.RequestException as e:
        logger.error(f"Request error while checking live status: {e}")
        return False, None, None, f"Network error: {str(e)}"
    except ParsingError as e:
        logger.error(f"Parsing error while checking live status: {e}")
        return False, None, None, str(e)
    except Exception as e:
        logger.error(f"Unexpected error while checking live status: {e}")
        return False, None, None, f"Unexpected error: {str(e)}"
