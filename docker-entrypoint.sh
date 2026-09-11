#!/bin/sh
# Runs database migrations and static collection before starting Gunicorn.
# Safe to run on every container start: migrate and collectstatic are both
# idempotent.
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --access-logfile - \
    --error-logfile -
