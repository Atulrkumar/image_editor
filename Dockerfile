FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install small set of system deps. Add more if you enable OCR (tesseract/opencv/etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy application
COPY . /app

# Create writable directories used by the app
RUN mkdir -p /app/uploads /app/generated

EXPOSE 5000

# Use gunicorn to serve the Flask app
CMD ["gunicorn", "app_free:app", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4"]
