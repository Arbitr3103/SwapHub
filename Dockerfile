# Базовый образ
FROM public.ecr.aws/docker/library/python:3.12-slim

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для приложения
RUN useradd -m appuser && chown -R appuser:appuser /home/appuser

# Установка рабочей директории
WORKDIR /app

# Копирование файлов проекта
COPY requirements.txt .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование остальных файлов проекта
COPY . .

# Создание необходимых директорий и настройка прав
RUN mkdir -p staticfiles media && \
    chown -R appuser:appuser /app

# Переключение на пользователя appuser
USER appuser

# Сбор статических файлов
RUN python manage.py collectstatic --noinput

# Открытие порта
EXPOSE 8000

# Запуск приложения через gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "SwapHub.wsgi:application", "--workers", "4"]
