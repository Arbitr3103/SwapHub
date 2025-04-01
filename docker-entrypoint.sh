#!/bin/bash

set -e

echo "Waiting for 5 seconds before starting..."
sleep 5

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py migrate

echo "Checking database state..."
USER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())")
echo "Current user count: $USER_COUNT"

if [ "$USER_COUNT" -eq "0" ]; then
    echo "Database is empty, loading initial data..."
    python manage.py loaddata db_dump.json
    
    # Проверяем, загрузились ли данные
    NEW_USER_COUNT=$(python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.count())")
    echo "Users after loading data: $NEW_USER_COUNT"
    
    ITEMS_COUNT=$(python manage.py shell -c "from items.models import Item; print(Item.objects.count())")
    echo "Items after loading data: $ITEMS_COUNT"
    
    # Проверяем изображения
    IMAGES_COUNT=$(python manage.py shell -c "from items.models import ItemImage; print(ItemImage.objects.count())")
    echo "Images after loading data: $IMAGES_COUNT"
    
    if [ "$NEW_USER_COUNT" -eq "0" ]; then
        echo "WARNING: Failed to load users from dump"
        cat db_dump.json
    fi
    
    # Если есть вещи, но нет изображений, запускаем скрипт создания тестовых данных
    if [ "$ITEMS_COUNT" -gt "0" ] && [ "$IMAGES_COUNT" -eq "0" ]; then
        echo "Items exist but no images found. Running create_test_data.py..."
        python create_test_data.py
    fi
else
    echo "Database already has users, skipping initial data load"
    ITEMS_COUNT=$(python manage.py shell -c "from items.models import Item; print(Item.objects.count())")
    echo "Current items count: $ITEMS_COUNT"
    
    # Проверяем изображения
    IMAGES_COUNT=$(python manage.py shell -c "from items.models import ItemImage; print(ItemImage.objects.count())")
    echo "Current images count: $IMAGES_COUNT"
    
    # Если есть вещи, но нет изображений, запускаем скрипт создания тестовых данных
    if [ "$ITEMS_COUNT" -gt "0" ] && [ "$IMAGES_COUNT" -eq "0" ]; then
        echo "Items exist but no images found. Running create_test_data.py..."
        python create_test_data.py
    fi
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
