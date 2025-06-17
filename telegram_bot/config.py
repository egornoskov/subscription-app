import os
from pathlib import Path

import environ


env = environ.Env()

BASE_DIR = Path(__file__).parent.parent
ENV_FILE = os.path.join(BASE_DIR, ".env")

if os.path.exists(ENV_FILE):
    environ.Env.read_env(ENV_FILE)
else:
    print(f"Warning: .env file not found at {ENV_FILE}. Relying on system environment variables.")


TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN", default=None)

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is not set or empty.")


POSTGRES_DB = env("POSTGRES_DB")
POSTGRES_USER = env("POSTGRES_USER")
POSTGRES_PASSWORD = env("POSTGRES_PASSWORD")
POSTGRES_HOST = env("POSTGRES_HOST")
POSTGRES_PORT = env("POSTGRES_PORT")


DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@" f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

BOT_WEB_SERVER_PORT = env.int(
    "BOT_WEB_SERVER_PORT",
    default=8001,
)

BOT_WEB_SERVER_SECRET_KEY = env(
    "BOT_WEB_SERVER_SECRET_KEY",
    default="very-secret-bot-key-for-django",
)
