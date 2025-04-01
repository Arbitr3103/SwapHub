#!/bin/bash

set -e

echo "Waiting for 5 seconds before starting..."
sleep 5

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

# Используем PORT из Render или 8000 по умолчанию
PORT="${PORT:-8000}"
echo "Starting Gunicorn on port $PORT..."

exec gunicorn SwapHub.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 4 \
    --log-level debug \
    --error-logfile - \
    --access-logfile - \
    --capture-output \
    --timeout 120
