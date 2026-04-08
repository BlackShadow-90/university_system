#!/bin/bash
set -e

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations (optional - can be done manually)
# python manage.py migrate

# Start the application
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
