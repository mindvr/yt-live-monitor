FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src

# Set environment variables
ENV POLL_FREQUENCY_MINUTES=30
ENV MONITORED_CHANNEL_ID=""
ENV TG_URL=""
ENV TG_ROUTE=""

# Expose port used by the web service
EXPOSE 8080

# Run the web service by default
CMD ["python", "-m", "src.main", "serve"]
