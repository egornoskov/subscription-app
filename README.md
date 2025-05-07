# Django Boilerplate

A lightweight Django boilerplate with PostgreSQL, Docker Compose, and Makefile for streamlined development.

---

## Features
- Django 5.2
- PostgreSQL database
- Docker Compose for containerized setup
- Makefile for common tasks
- Environment variable configuration via `.env`

---

## Project Structure
```
django-example-py3.13/
├── core/                   # Django project files
│   ├── project/
│   │   ├── settings/
│   │   │   ├── main.py    # Core Django settings
│   │   │   ├── local.py   # Local development settings
├── docker_compose/         # Docker Compose configs
│   ├── app.yaml           # Django app
│   ├── storages.yaml      # PostgreSQL
├── static/                 # Collected static files
├── .env                    # Environment variables
├── Dockerfile              # Django app image
├── entrypoint.sh           # Container entry script
├── manage.py               # Django management
├── Makefile                # Task automation
└── README.md
```

---

## Prerequisites
- Docker and Docker Compose
- Make (available on Linux/macOS; use WSL/MinGW on Windows)

---

## Setup and Startup
Follow these steps to start the application:

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd django-example-py3.13
   ```

2. **Configure `.env`**:
   Copy `.env.example` to `.env` and update:
   ```
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_PORT=8000
   POSTGRES_DB=mydatabase
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=yourpassword
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   ```

3. **Create `local.py`**:
   In `core/project/settings/`, create `local.py` to override `main.py` settings for local development:
   ```python
   from .main import *

   DEBUG = True
   ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
   ```
   This enables debug mode and allows local access.

4. **Build and start containers**:
   ```bash
   make app
   ```
   This starts:
   - Django app (`http://localhost:8000`)
   - PostgreSQL database (`localhost:5432`)

5. **Apply database migrations**:
   ```bash
   make migrate
   ```

6. **Collect static files**:
   ```bash
   make collectstatic
   ```

7. **Create superuser** (optional, for admin access):
   ```bash
   make superuser
   ```
   Access the admin panel at `http://localhost:8000/admin/`.

---

## Makefile Commands
The `Makefile` provides commands for managing the project:
- `make storages`: Starts the PostgreSQL container.
- `make storages-logs`: Shows PostgreSQL logs.
- `make storages-down`: Stops and removes the PostgreSQL container.
- `make database`: Opens a PostgreSQL CLI (`psql`).
- `make app`: Starts Django and PostgreSQL containers.
- `make app-logs`: Shows Django logs.
- `make app-down`: Stops and removes all containers.
- `make app-shell`: Opens a shell in the Django container.
- `make migrate`: Applies Django migrations.
- `make migrations`: Creates new Django migration files.
- `make superuser`: Creates a Django admin superuser.
- `make collectstatic`: Collects static files to `static/`.

---

## PostgreSQL Access
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `mydatabase` (or `POSTGRES_DB`)
- **User**: `postgres` (or `POSTGRES_USER`)
- **Password**: `yourpassword` (or `POSTGRES_PASSWORD`)

**VS Code**:
1. Install **PostgreSQL** extension (`ckolkman.vscode-postgres`).
2. Add connection in **PostgreSQL Explorer** using the above credentials.

---

## Troubleshooting
- **Container issues**: Check logs (`make app-logs`, `make storages-logs`).
- **Database errors**: Verify `.env` and test connection (`make database`).
- **Static files**: Ensure `make collectstatic` ran and `STATIC_ROOT` is set.

---

## License
MIT License. See `LICENSE` for details.

---

# Django Boilerplate (Русский)

Лёгкий шаблон для Django с PostgreSQL, Docker Compose и Makefile для упрощения разработки.

---

## Возможности
- Django 5.2
- База данных PostgreSQL
- Docker Compose для контейнеризации
- Makefile для типовых задач
- Настройка через переменные окружения в `.env`

---

## Структура проекта
```
django-example-py3.13/
├── core/                   # Файлы Django проекта
│   ├── project/
│   │   ├── settings/
│   │   │   ├── main.py    # Основные настройки Django
│   │   │   ├── local.py   # Настройки для локальной разработки
├── docker_compose/         # Конфигурации Docker Compose
│   ├── app.yaml           # Приложение Django
│   ├── storages.yaml      # PostgreSQL
├── static/                 # Собранные статические файлы
├── .env                    # Переменные окружения
├── Dockerfile              # Образ для Django
├── entrypoint.sh           # Скрипт запуска контейнера
├── manage.py               # Управление Django
├── Makefile                # Автоматизация задач
└── README.md
```

---

## Требования
- Docker и Docker Compose
- Make (доступен на Linux/macOS; используйте WSL/MinGW на Windows)

---

## Установка и запуск
Для запуска приложения выполните шаги:

1. **Клонируйте репозиторий**:
   ```bash
   git clone <repository-url>
   cd django-example-py3.13
   ```

2. **Настройте `.env`**:
   Скопируйте `.env.example` в `.env` и обновите:
   ```
   DJANGO_SECRET_KEY=your-secret-key
   DJANGO_PORT=8000
   POSTGRES_DB=mydatabase
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=yourpassword
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432
   ```

3. **Создайте `local.py`**:
   В папке `core/project/settings/` создайте `local.py` для переопределения настроек из `main.py`:
   ```python
   from .main import *

   DEBUG = True
   ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
   ```
   Это включает режим отладки и разрешает локальный доступ.

4. **Соберите и запустите контейнеры**:
   ```bash
   make app
   ```
   Запускает:
   - Приложение Django (`http://localhost:8000`)
   - Базу данных PostgreSQL (`localhost:5432`)

5. **Примените миграции базы данных**:
   ```bash
   make migrate
   ```

6. **Соберите статические файлы**:
   ```bash
   make collectstatic
   ```

7. **Создайте суперпользователя** (опционально, для доступа к админке):
   ```bash
   make superuser
   ```
   Админка доступна по адресу `http://localhost:8000/admin/`.

---

## Команды Makefile
`Makefile` предоставляет команды для управления проектом:
- `make storages`: Запускает контейнер PostgreSQL.
- `make storages-logs`: Показывает логи PostgreSQL.
- `make storages-down`: Останавливает и удаляет контейнер PostgreSQL.
- `make database`: Открывает CLI PostgreSQL (`psql`).
- `make app`: Запускает контейнеры Django и PostgreSQL.
- `make app-logs`: Показывает логи Django.
- `make app-down`: Останавливает и удаляет все контейнеры.
- `make app-shell`: Открывает shell в контейнере Django.
- `make migrate`: Применяет миграции Django.
- `make migrations`: Создаёт новые файлы миграций Django.
- `make superuser`: Создаёт суперпользователя Django.
- `make collectstatic`: Собирает статические файлы в `static/`.

---

## Доступ к PostgreSQL
- **Хост**: `localhost`
- **Порт**: `5432`
- **База данных**: `mydatabase` (или `POSTGRES_DB`)
- **Пользователь**: `postgres` (или `POSTGRES_USER`)
- **Пароль**: `yourpassword` (или `POSTGRES_PASSWORD`)

**VS Code**:
1. Установите расширение **PostgreSQL** (`ckolkman.vscode-postgres`).
2. Добавьте подключение в **PostgreSQL Explorer** с указанными данными.

---

## Устранение неполадок
- **Проблемы с контейнерами**: Проверьте логи (`make app-logs`, `make storages-logs`).
- **Ошибки базы данных**: Проверьте `.env` и протестируйте подключение (`make database`).
- **Статические файлы**: Убедитесь, что `make collectstatic` выполнен и `STATIC_ROOT` настроен.

---

## Лицензия
Лицензия MIT. См. файл `LICENSE` для деталей.