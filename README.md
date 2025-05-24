# YouTube Livestream Checker

A utility to check if a YouTube channel is currently livestreaming and extract the direct link to that stream.

## Problem Statement

Some YouTube channels keep their past livestreams as unlisted videos, making them difficult to find if you miss the livestream due to timezone differences. This tool helps by checking if a channel is currently live and providing the direct link to the livestream.

## Features

- Check if a YouTube channel is currently livestreaming
- Extract the direct link to active livestreams
- Convert YouTube channel URLs to channel IDs
- Command-line interface for quick checks
- HTTP API for integration with other applications
- Docker support for easy deployment

## Installation

### Using Python

```bash
# Clone the repository
git clone https://github.com/mindvr/yt-live-monitor.git
cd yt-live-monitor

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Using Docker

```bash
# Build the Docker image
docker build -t yt-live-checker:latest .

# Run the container
docker run -p 8080:8080 --name yt-live-checker --rm yt-live-checker:latest
```

## Usage

### Command-line Interface

```bash
# Check if a channel is livestreaming using a channel ID
python -m src.main check-live UCj-Xm8j6WBgKY8OG7s9r2vQ

# Check if a channel is livestreaming using a channel URL or handle
python -m src.main check-live https://www.youtube.com/@ChannelName

# Get a channel ID from a URL or handle
python -m src.main get-channel-id https://www.youtube.com/@ChannelName
```

### HTTP API

Start the web service:

```bash
python -m src.main serve
```

The service will be available at `http://localhost:8080`.

#### API Endpoints

- `GET /status` - Check API health
- `GET /check-live/{channel_id}` - Check if a channel is livestreaming by ID
- `POST /check-live` - Check if a channel is livestreaming by URL or handle
- `POST /get-channel-id` - Extract a channel ID from a YouTube URL or handle

Example request:
```bash
curl http://localhost:8080/check-live/UCj-Xm8j6WBgKY8OG7s9r2vQ
```

Example response:
```json
{
  "channel_id": "UCj-Xm8j6WBgKY8OG7s9r2vQ",
  "is_live": true,
  "livestream_url": "https://www.youtube.com/watch?v=czoEAKX9aaM",
  "checked_at": "2023-09-14T12:34:56Z"
}
```

## Development

### Setup Development Environment

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## License

MIT
