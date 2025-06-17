from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from telegram_bot.config import DATABASE_URL


async_engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)
