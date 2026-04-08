FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        pkg-config \
        default-libmysqlclient-dev \
        build-essential \
        libmariadb-dev \
        libmariadb-dev-compat \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN echo "Build timestamp: $(date)" && pip install -r requirements.txt

# Copy application code
COPY . .

# Collect static files (skip if fails)
RUN python manage.py collectstatic --noinput || echo "Static files collection skipped"

# Expose port
EXPOSE 8000

# Run the application
CMD python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
