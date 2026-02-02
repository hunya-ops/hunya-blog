FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=run.py

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Create upload and data directories with correct permissions
RUN mkdir -p app/static/uploads instance data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Run with Gunicorn (Shell form to allow variable expansion)
CMD gunicorn -w ${GUNICORN_WORKERS:-4} -b ${GUNICORN_BIND:-0.0.0.0:5000} run:app
