FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies for OCR and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app

# Create writable directories used by the app
RUN mkdir -p /app/uploads /app/generated

# Render uses PORT environment variable, default to 10000
ENV PORT=10000
EXPOSE ${PORT}

# Use gunicorn to serve the Flask app
CMD gunicorn app_free:app --bind 0.0.0.0:${PORT} --workers 1 --threads 4 --timeout 120
