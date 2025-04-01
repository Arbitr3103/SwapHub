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

# Создание и активация виртуального окружения
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

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

# Открытие порта
EXPOSE 8000

# Создание скрипта запуска
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Запуск приложения через entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
