#!/bin/bash

set -e

echo "Waiting for 5 seconds before starting..."
sleep 5

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

# Загрузка начальных данных, если база пустая
if [ "$(python manage.py dumpdata auth.User --indent 2 | grep '\[]')" ]; then
    echo "Loading initial data..."
    python manage.py loaddata db_dump.json
fi

# Используем PORT из Render или 10000 по умолчанию
PORT="${PORT:-10000}"
echo "Starting Gunicorn on port $PORT..."

exec gunicorn SwapHub.wsgi:application \
    --bind "0.0.0.0:$PORT" \
    --workers 2 \
    --threads 4 \
    --worker-class=gthread \
    --worker-tmp-dir /dev/shm \
    --log-level info \
    --error-logfile - \
    --access-logfile - \
    --capture-output
