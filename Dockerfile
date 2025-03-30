# Базовый образ для сборки
FROM python:3.12-slim as builder

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка poetry для управления зависимостями
RUN pip install --no-cache-dir poetry

# Установка рабочей директории
WORKDIR /app

# Копирование файлов зависимостей
COPY requirements.txt .

# Установка зависимостей
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Финальный образ
FROM python:3.12-slim

# Установка необходимых runtime пакетов
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для приложения
RUN useradd -m appuser && chown -R appuser:appuser /home/appuser

# Установка рабочей директории
WORKDIR /app

# Копирование wheels из builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Установка зависимостей
RUN pip install --no-cache /wheels/*

# Копирование кода приложения
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
