#!/bin/bash

# Сбор статических файлов
python manage.py collectstatic --noinput

# Применение миграций
python manage.py migrate

# Запуск Gunicorn
exec gunicorn --bind 0.0.0.0:8000 SwapHub.wsgi:application --workers 4
