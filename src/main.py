"""
Main module for YouTube Livestream Checker.

This module provides the entry point for both the command-line interface
and the web service.
"""
import sys
import json
import logging
from typing import Optional
import click

from .youtube_service import YouTubeService
from .web_service import run_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """YouTube Livestream Checker - Check if a YouTube channel is currently livestreaming."""
    pass


@cli.command(name="check-live")
@click.argument("channel_id_or_url", type=str)
@click.option("--json-output", is_flag=True, help="Output results in JSON format")
def check_live(channel_id_or_url: str, json_output: bool):
    """
    Check if a YouTube channel is currently livestreaming.

    CHANNEL_ID_OR_URL: YouTube channel ID, URL, or handle to check
    """
    try:
        result = YouTubeService.check_if_live(channel_id_or_url)

        if json_output:
            # Output in JSON format
            print(json.dumps(result, indent=2))
            return

        # Output in human-readable format
        print(f"Channel ID: {result.get('channel_id', 'Unknown')}")

        if result.get("error"):
            print(f"Error: {result['error']}")
            return

        if result["is_live"]:
            print("Status: LIVE")
            if "title" in result:
                print(f"Title: {result['title']}")
            print(f"Livestream URL: {result['livestream_url']}")
        else:
            print("Status: NOT LIVE")

        print(f"Checked at: {result['checked_at']}")

    except Exception as e:
        logger.error(f"Error: {e}")
        if json_output:
            error_result = {
                "error": str(e),
                "is_live": False,
                "checked_at": None
            }
            print(json.dumps(error_result, indent=2))
        else:
            print(f"Error: {e}")
        sys.exit(1)


@cli.command(name="serve")
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", default=8080, help="Port to bind the server to")
def serve(host: str, port: int):
    """Start the web service."""
    print(f"Starting YouTube Livestream Checker web service on {host}:{port}")
    run_server(host, port)


@cli.command(name="get-channel-id")
@click.argument("url", type=str)
def get_channel_id(url: str):
    """
    Extract a channel ID from a YouTube URL or handle.

    URL: YouTube URL or handle to extract channel ID from
    """
    try:
        channel_id = YouTubeService.get_channel_id(url)
        print(f"Channel ID: {channel_id}")
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
