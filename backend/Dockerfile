# Stage 1: Builder - Install dependencies
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime - Minimal production image
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install runtime dependencies for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY src/ ./src/
COPY main.py ./
COPY init_db.py ./

# Set Python path so imports work correctly
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose the API port (HF Spaces requires 7860)
EXPOSE 7860

# Switch to non-root user
USER appuser

# Run init_db then start the FastAPI server on port 7860
CMD ["sh", "-c", "python init_db.py && uvicorn src.main:app --host 0.0.0.0 --port 7860"]
