# backend/Dockerfile
FROM python:3.12-slim

# Work dir for build steps
WORKDIR /app

# Install minimal system deps needed by TF / Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy repo into container (Render's build context is repo root)
COPY . /app/

# Install Python deps (assume backend/requirements.txt exists)
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set envs
ENV MODEL_PATH=/app/model.keras
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose (kept for clarity)
EXPOSE 8000

# Ensure we run from the backend folder and allow shell expansion for $PORT
# Use 1 worker for TF memory reasons; threads provide concurrency.
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--chdir", "/app", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
