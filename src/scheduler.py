import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.channel_parser import check_channel_live_status
from src.notifier import notify_live_stream, notify_error

logger = logging.getLogger(__name__)


async def check_channel():
    logger.info("Checking Channel")

    channel_id = os.getenv("MONITORED_CHANNEL_ID")
    if not channel_id:
        return

    is_live, livestream_url, title, error = check_channel_live_status(channel_id)

    if error:
        notify_error(error)
        return
    elif is_live and livestream_url and title:
        notify_live_stream(livestream_url, title)


async def run_scheduled_task():
    interval = int(os.getenv("POLL_FREQUENCY_MINUTES", "30")) * 60
    while True:
        try:
            await check_channel()
        except Exception as e:
            logger.error(f"Error in scheduled task: {e}")

        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_scheduled_task())
    logger.info("Scheduled task registered and started")

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Scheduled task cancelled")
