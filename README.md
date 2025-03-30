# SwapHub

SwapHub - это веб-приложение для обмена и аренды вещей, разработанное на Django.

## Основные функции

- Регистрация и аутентификация пользователей
- Управление профилем пользователя
- Добавление предметов для обмена/аренды
- Система друзей и уведомлений
- Запросы на обмен и аренду предметов
- Система отзывов и рейтингов

## Технологии

- Python 3.12
- Django
- PostgreSQL
- Docker & Docker Compose
- Bootstrap 5
- GitHub Actions для CI/CD

## Запуск проекта

1. Клонировать репозиторий:
```bash
git clone https://github.com/Arbitr3103/SwapHub.git
cd SwapHub
```

2. Создать файл .env на основе .env.example:
```bash
cp .env.example .env
```

3. Запустить через Docker Compose:
```bash
docker compose up -d
```

4. Создать тестовые данные (опционально):
```bash
docker compose exec web python manage.py create_test_data
```

## Тестовые пользователи

После создания тестовых данных доступны следующие пользователи:
- alice (пароль: testpass123)
- bob (пароль: testpass123)
- charlie (пароль: testpass123)
- diana (пароль: testpass123)
- evan (пароль: testpass123)
