#!/bin/bash

set -e

echo "Waiting for 5 seconds before starting..."
sleep 5

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Starting Gunicorn..."
exec gunicorn SwapHub.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --log-level debug \
    --error-logfile - \
    --access-logfile - \
    --capture-output \
    --timeout 120
