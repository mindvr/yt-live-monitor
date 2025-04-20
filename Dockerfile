FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port used by the web service
EXPOSE 8080

# Run the web service by default
CMD ["python", "-m", "src.main", "serve"]