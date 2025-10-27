# Use slim Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Pillow and TensorFlow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model
# When Render builds from backend/ directory, files are at root of build context
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables
ENV MODEL_PATH=model.keras
ENV PYTHONUNBUFFERED=1

# Run with gunicorn for production
# Using 1 worker to avoid duplicate TF memory allocation
# Using 4 threads for concurrent request handling
# Render sets PORT dynamically, default to 8000 for local
# Use --chdir to ensure gunicorn runs from /app directory
CMD gunicorn -k uvicorn.workers.UvicornWorker main:app \
    --chdir /app \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --threads 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
