"""
Dockerfile — Multi-stage build for FastAPI backend & scheduler.
"""
FROM python:3.11-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no dev deps in production)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --without dev

# Copy application code
COPY . .

# Create data directory for ChromaDB
RUN mkdir -p /app/data/chromadb

EXPOSE 8000

# Default command: FastAPI API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
