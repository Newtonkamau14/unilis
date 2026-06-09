FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install \
    --no-cache-dir \
    -r requirements.txt

COPY . .

RUN mkdir -p outputs/explainability

EXPOSE 8011

HEALTHCHECK --interval=30s \
    --timeout=10s \
    --start-period=10s \
    --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8011/health')" || exit 1

CMD [
    "uvicorn",
    "app:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8011",
    "--workers",
    "1"
]
