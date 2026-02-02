FROM python:3.13-slim

WORKDIR /app

# Install system dependencies and gosu
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    gosu \
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

# Create directories perms
RUN mkdir -p app/static/uploads instance data

# Copy entrypoint script
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose port
EXPOSE 5000

# Set entrypoint to handling permission fixing
ENTRYPOINT ["entrypoint.sh"]

# default CMD which will be passed to entrypoint
CMD gunicorn -w ${GUNICORN_WORKERS:-4} -b ${GUNICORN_BIND:-0.0.0.0:5000} run:app
