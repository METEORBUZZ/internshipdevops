# ==============================================================================
# Dockerfile: Production-ready Python Flask Container
# ==============================================================================
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

# Set working directory
WORKDIR /app

# Create a non-privileged user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Install system dependencies (curl for healthcheck, gcc & python3-dev to compile psutil)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app/ ./

# Change ownership to the non-root user
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose service port
EXPOSE 5000

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Launch application with production Gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
