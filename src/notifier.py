import logging
import os
import requests

logger = logging.getLogger(__name__)

def _send_telegram_notification(message: str):
    tg_url = os.environ.get('TG_URL')
    tg_route = os.environ.get('TG_ROUTE')
    if not tg_url or not tg_route:
        logger.warning("TG_URL or TG_ROUTE environment variables are not set. Skipping notification.")
        return
    bot_id, chat_id = tg_route.split(':')
    payload = {
        "botId": bot_id,
        "chatId": chat_id,
        "message": message
    }
    response = requests.post(tg_url, json=payload)
    if not response.ok:
        logger.error(f"Failed to send notification. Status code: {response.status_code}, Response: {response.text}")


def notify_live_stream(livestream_url: str, title: str):
    message = f"{title}\n{livestream_url}"
    _send_telegram_notification(message)


def notify_error(error_message: str):
    message = f"unexpected error occurred:\n```\n{error_message}\n```"
    _send_telegram_notification(message)
