# README

## О проекте

Приложение для управления подписками и заказами с атомарной моделью пользователя.

---

## Функционал

- Управление подписками и заказами
- Атомарная модель пользователя
- JWT-аутентификация
- Кастомный middleware для ограничения доступа к заказам без активной подписки (`core/project/middleware/subscription_middleware.py`)
- Кастомный permission для управления доступом (`core/project/permissions.py`)
- IoC-контейнер на основе **Punq** (`core/project/containers.py`)
- Кастомная пагинация (`core/api/schemas/pagination.py`)
- Кастомная схема ответа API (`core/api/schemas/response_schemas.py`, `core/api/utils/response_builder.py`)
- Поиск с использованием кастомных фильтров (`core/api/*/schemas/filters.py`)
- Telegram-бот для подтверждения регистрации и уведомлений о создании заказа (`telegram_bot/`), использующий асинхронную **SQLAlchemy** для работы с базой данных
- Swagger-документация API

---

## Структура проекта

- `core/api/v1/`: API-эндпоинты версии 1 (модули `products`, `subscriptions`, `tariff`, `users` с маршрутами в `urls.py` и обработчиками в `handlers.py`)
- `core/apps/`: Django-приложения (`products`, `subscriptions`, `tariff`, `user`, `common`) с моделями, сервисами и сериализаторами
- `core/project/middleware/`: Кастомный middleware (`subscription_middleware.py`)
- `core/project/permissions.py`: Кастомные permission-классы
- `core/project/containers.py`: IoC-контейнер (используется **Punq**)
- `telegram_bot/`: Telegram-бот для уведомлений и подтверждения регистрации
- `docker_compose/`: Docker Compose файлы для запуска приложения, хранилищ и бота
- `static/admin/`: Статические файлы для Django-админки
- `check/`: Видео и скриншоты, демонстрирующие работу приложения

---

## Технологии

- **Backend**: Django, Python
- **Аутентификация**: JWT
- **IoC**: Punq
- **API**: Django REST Framework, Swagger-документация
- **Сборка**: Docker, Docker Compose
- **Бот**: Telegram API, асинхронная SQLAlchemy
- **Инструменты**: Poetry, pre-commit, Celery
- **База данных**: PostgreSQL
- **Кэширование/Очереди**: Redis

---


## Makefile
- **Команды** для упрощения работы:
- `make network`: Создает Docker-сеть `network_for_subscriptions`
- `make clean-network`: Удаляет Docker-сеть `network_for_subscriptions`
- `make storages`: Запускает сервисы хранилищ (PostgreSQL, Redis) из `docker_compose/storages.yaml`
- `make storages-logs`: Показывает логи контейнера базы данных (`subscriptions_db`)
- `make storages-down`: Останавливает и удаляет сервисы хранилищ
- `make database`: Открывает интерактивную сессию `psql` в контейнере базы данных
- `make app`: Запускает приложение и хранилища из `docker_compose/app.yaml` и `docker_compose/storages.yaml`
- `make logs`: Показывает логи контейнера приложения (`subscriptions_main_app`)
- `make app-down`: Останавливает и удаляет сервисы приложения и хранилищ
- `make app-shell`: Открывает интерактивную оболочку (`ash`) в контейнере приложения
- `make migrate`: Выполняет миграции базы данных
- `make migrations`: Создает новые миграции
- `make superuser`: Создает суперпользователя Django
- `make collectstatic`: Собирает статические файлы
- `make show`: Показывает список миграций
- `make reload`: Перезапускает приложение и бота
- `make bot`: Запускает Telegram-бот из `docker_compose/tg_bot.yaml`
- `make bot-down`: Останавливает и удаляет сервисы бота
- `make bot-shell`: Открывает интерактивную оболочку (`bash`) в контейнере бота
- `make bot-logs`: Показывает логи контейнера бота (`subscriptions_telegram_bot`)
- `make all`: Запускает все сервисы (приложение, хранилища, бот)
- `make down-all`: Останавливает и удаляет все сервисы
- `make restart-all`: Перезапускает все сервисы
- `make logs-all`: Показывает объединенные логи всех сервисов

---


## Установка

- Клонируйте репозиторий:
  ```bash
  git clone <URL_репозитория>
  ```

- Создайте .env файл:
DJANGO_SECRET_KEY=your_keu
POSTGRES_DB=your_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_pswd
POSTGRES_HOST=your_host
POSTGRES_PORT=your_port
DJANGO_PORT=your_port_for_django
TELEGRAM_BOT_TOKEN=your_token
BOT_API_KEY=your_api_key
BOT_WEB_SERVER_PORT=your_bot_port
BOT_WEB_SERVER_SECRET_KEY=your_web_server


- Создайте файл core/project/settings/local.py со следующим содержимым:
```
from .main import *  # noqa

DEBUG = True
```

- Запустите приложение использую команды из makefile:
  ```bash
  make network
  make all
  ```