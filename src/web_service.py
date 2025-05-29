"""
Web service module for YouTube Livestream Checker.

This module provides a FastAPI-based HTTP API for checking
if a YouTube channel is currently livestreaming.
"""
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, Path, Query
from pydantic import BaseModel, Field, validator
import uvicorn

from .youtube_service import YouTubeService, ParsingError
from .scheduler import lifespan

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="YouTube Livestream Checker",
    description="Check if a YouTube channel is currently livestreaming",
    version="1.0.0",
    lifespan=lifespan
)


# Define request and response models
class ChannelUrlRequest(BaseModel):
    url: str = Field(..., description="YouTube channel URL or handle")


class LivestreamCheckResponse(BaseModel):
    channel_id: Optional[str] = Field(None, description="The channel ID that was checked")
    channel_id_or_url: Optional[str] = Field(None, description="The original input if channel ID extraction failed")
    is_live: bool = Field(..., description="Whether the channel is currently livestreaming")
    livestream_url: Optional[str] = Field(None, description="The URL of the livestream if live")
    title: Optional[str] = Field(None, description="The title of the livestream if live")
    error: Optional[str] = Field(None, description="Error message if applicable")
    checked_at: str = Field(..., description="Timestamp of when the check was performed")


# Define API routes
@app.get("/status")
async def get_status() -> Dict[str, str]:
    """
    Check the health status of the API.

    Returns:
        dict: Status information
    """
    return {"status": "ok", "service": "YouTube Livestream Checker"}


@app.get("/check-live/{channel_id}", response_model=LivestreamCheckResponse)
async def check_live_by_id(
        channel_id: str = Path(..., description="YouTube channel ID")
) -> Dict[str, Any]:
    """
    Check if a channel is livestreaming by channel ID.

    Args:
        channel_id: The YouTube channel ID to check

    Returns:
        dict: Livestream check result

    Raises:
        HTTPException: If the check fails
    """
    try:
        result = YouTubeService.check_if_live(channel_id)
        return result
    except Exception as e:
        logger.error(f"Error checking live status for channel ID {channel_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-live", response_model=LivestreamCheckResponse)
async def check_live_by_url(
        request: ChannelUrlRequest = Body(..., description="YouTube channel URL or handle")
) -> Dict[str, Any]:
    """
    Check if a channel is livestreaming by URL or handle.

    Args:
        request: Request body containing the channel URL or handle

    Returns:
        dict: Livestream check result

    Raises:
        HTTPException: If the check fails
    """
    try:
        result = YouTubeService.check_if_live(request.url)
        return result
    except Exception as e:
        logger.error(f"Error checking live status for URL {request.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get-channel-id", response_model=Dict[str, str])
async def get_channel_id_by_post(
        request: ChannelUrlRequest = Body(..., description="YouTube URL or handle to extract channel ID from")
) -> Dict[str, str]:
    """
    Extract a channel ID from a YouTube URL or handle using POST.

    Args:
        request: Request body containing the YouTube URL or handle

    Returns:
        dict: Dictionary containing the extracted channel ID

    Raises:
        HTTPException: If the extraction fails
    """
    try:
        channel_id = YouTubeService.get_channel_id(request.url)
        return {"channel_id": channel_id}
    except Exception as e:
        logger.error(f"Error extracting channel ID from {request.url}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def run_server(host: str = "0.0.0.0", port: int = 8080):
    """
    Run the FastAPI web server.

    Args:
        host: Host to bind the server to
        port: Port to bind the server to
    """
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
