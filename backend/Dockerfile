# backend/Dockerfile  (or put at repo root but keep paths consistent)
FROM python:3.12-slim

# Workdir should be where main.py will live
WORKDIR /app

# Minimal system deps (your original)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy backend folder contents into /app so main.py is /app/main.py
# Using COPY backend/ /app/ is robust if build context is repo root or backend.
COPY backend/ /app/

RUN echo "==== /app listing ====" && ls -la /app && echo "==== recursive ====" && ls -laR /app

# If you prefer build context=backend then COPY . /app/ also works.
RUN pip install --no-cache-dir -r /app/requirements.txt

ENV MODEL_PATH=/app/model.keras
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

EXPOSE 8000

# Use exec JSON form so signals pass through; this assumes main.py is in /app
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", \
     "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4", \
     "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
