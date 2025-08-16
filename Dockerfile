# Multi-stage build for production
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set work directory
WORKDIR /app

# Install Python dependencies
COPY PMS/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r django && useradd -r -g django django

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=PMS.settings_production_clean
ENV DEBUG=0

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project files - maintain Django project structure
COPY PMS/ ./

# Copy existing database if it exists (optional)
COPY database_backup.sqlite3 ./

# Copy startup script
COPY start.sh .
RUN chmod +x start.sh

# Create necessary directories
RUN mkdir -p staticfiles media data logs

# Create data directory that will be mounted and set permissions
RUN mkdir -p /app/data && chmod 755 /app/data

# Change ownership to django user
RUN chown -R django:django /app

# Don't switch to django user yet - let startup script handle permissions
# USER django

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/admin/ || exit 1

# Run startup script
CMD ["./start.sh"]
